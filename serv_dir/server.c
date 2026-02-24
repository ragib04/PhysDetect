#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

#define PORT 60000
#define BACKLOG 1
#define FILENAME_SIZE 256
#define BUFFER_SIZE 4096

static int ssl_read_all(SSL *ssl, void *buf, size_t len) {
    size_t total = 0;
    unsigned char *p = buf;

    while (total < len) {
        int n = SSL_read(ssl, p + total, len - total);
        if (n <= 0) {
            return -1;
        }
        total += n;
    }
    return 0;
}

int main(void) {
  signal(SIGPIPE, SIG_IGN);
    int server_fd = -1, client_fd = -1;
    struct sockaddr_in server_addr;

    SSL_CTX *ctx = NULL;
    SSL *ssl = NULL;

    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_ssl_algorithms();

    ctx = SSL_CTX_new(TLS_server_method());
    if (!ctx) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    if (SSL_CTX_use_certificate_file(ctx, "server.crt", SSL_FILETYPE_PEM) <= 0 ||
        SSL_CTX_use_PrivateKey_file(ctx, "server.key", SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        goto cleanup;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind");
        goto cleanup;
    }

    if (listen(server_fd, BACKLOG) < 0) {
        perror("listen");
        goto cleanup;
    }

    printf("TLS server listening on port %d...\n", PORT);

    client_fd = accept(server_fd, NULL, NULL);
    if (client_fd < 0) {
        perror("accept");
        goto cleanup;
    }

    ssl = SSL_new(ctx);
    SSL_set_fd(ssl, client_fd);

    if (SSL_accept(ssl) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("TLS client connected using %s\n", SSL_get_cipher(ssl));

    char filename[FILENAME_SIZE + 1];
    memset(filename, 0, sizeof(filename));

    if (ssl_read_all(ssl, filename, FILENAME_SIZE) < 0) {
        fprintf(stderr, "Failed to read filename\n");
        goto cleanup;
    }

    filename[FILENAME_SIZE] = '\0';

    uint32_t net_size;
    if (ssl_read_all(ssl, &net_size, sizeof(net_size)) < 0) {
        fprintf(stderr, "Failed to read file size\n");
        goto cleanup;
    }

    uint32_t file_size = ntohl(net_size);
    printf("Receiving '%s' (%u bytes)\n", filename, file_size);

    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        perror("fopen");
        goto cleanup;
    }

    uint8_t buffer[BUFFER_SIZE];
    uint32_t remaining = file_size;

    while (remaining > 0) {
        size_t chunk = remaining < BUFFER_SIZE ? remaining : BUFFER_SIZE;
        if (ssl_read_all(ssl, buffer, chunk) < 0) {
            fprintf(stderr, "Failed during file receive\n");
            fclose(fp);
            goto cleanup;
        }
        fwrite(buffer, 1, chunk, fp);
        remaining -= chunk;
    }

    fclose(fp);
    printf("File saved successfully.\n");

cleanup:
    if (ssl) {
        SSL_shutdown(ssl);
        SSL_free(ssl);
    }
    if (client_fd >= 0) close(client_fd);
    if (server_fd >= 0) close(server_fd);
    if (ctx) SSL_CTX_free(ctx);

    EVP_cleanup();
    return 0;
}
