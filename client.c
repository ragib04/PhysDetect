// tls_file_client.c
// Usage: ./tls_client <server_ip> <file_path>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/stat.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

#define PORT 60000
#define FILENAME_SIZE 256
#define BUFFER_SIZE 4096

static int ssl_write_all(SSL *ssl, const void *buf, size_t len) {
    size_t total = 0;
    const unsigned char *p = buf;

    while (total < len) {
        int n = SSL_write(ssl, p + total, len - total);
        if (n <= 0) {
            return -1;
        }
        total += n;
    }
    return 0;
}

static const char *basename_simple(const char *path) {
    const char *slash = strrchr(path, '/');
    return slash ? slash + 1 : path;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <server_ip> <file_path>\n", argv[0]);
        return 1;
    }

    const char *server_ip = argv[1];
    const char *file_path = argv[2];

    /* ---- Open file ---- */
    FILE *fp = fopen(file_path, "rb");
    if (!fp) {
        perror("fopen");
        return 1;
    }

    struct stat st;
    if (stat(file_path, &st) < 0) {
        perror("stat");
        fclose(fp);
        return 1;
    }

    if (st.st_size > UINT32_MAX) {
        fprintf(stderr, "File too large\n");
        fclose(fp);
        return 1;
    }

    uint32_t file_size = (uint32_t)st.st_size;
    const char *filename = basename_simple(file_path);

    /* ---- OpenSSL init ---- */
    SSL_library_init();
    SSL_load_error_strings();
    OpenSSL_add_ssl_algorithms();

    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        ERR_print_errors_fp(stderr);
        fclose(fp);
        return 1;
    }

    /* ---- Optional: verify server cert ---- */
    SSL_CTX_set_verify(ctx, SSL_VERIFY_NONE, NULL);
    // For real security:
    // SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, NULL);
    // SSL_CTX_load_verify_locations(ctx, "server.crt", NULL);

    /* ---- Socket ---- */
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        goto cleanup;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, server_ip, &addr.sin_addr) != 1) {
        fprintf(stderr, "Invalid server IP\n");
        goto cleanup;
    }

    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("connect");
        goto cleanup;
    }

    /* ---- TLS handshake ---- */
    SSL *ssl = SSL_new(ctx);
    SSL_set_fd(ssl, sock);

    if (SSL_connect(ssl) <= 0) {
        ERR_print_errors_fp(stderr);
        goto cleanup;
    }

    printf("Connected using %s\n", SSL_get_cipher(ssl));

    /* ---- Send filename (256 bytes) ---- */
    char fname_buf[FILENAME_SIZE];
    memset(fname_buf, 0, sizeof(fname_buf));
    strncpy(fname_buf, filename, FILENAME_SIZE - 1);

    if (ssl_write_all(ssl, fname_buf, FILENAME_SIZE) < 0) {
        fprintf(stderr, "Failed to send filename\n");
        goto cleanup_ssl;
    }

    /* ---- Send file size ---- */
    uint32_t net_size = htonl(file_size);
    if (ssl_write_all(ssl, &net_size, sizeof(net_size)) < 0) {
        fprintf(stderr, "Failed to send file size\n");
        goto cleanup_ssl;
    }

    /* ---- Send file data ---- */
    unsigned char buffer[BUFFER_SIZE];
    size_t n;

    while ((n = fread(buffer, 1, BUFFER_SIZE, fp)) > 0) {
        if (ssl_write_all(ssl, buffer, n) < 0) {
            fprintf(stderr, "Failed during file send\n");
            goto cleanup_ssl;
        }
    }

    printf("File sent successfully.\n");

cleanup_ssl:
    SSL_shutdown(ssl);
    SSL_free(ssl);

cleanup:
    close(sock);
    SSL_CTX_free(ctx);
    fclose(fp);
    EVP_cleanup();
    return 0;
}
