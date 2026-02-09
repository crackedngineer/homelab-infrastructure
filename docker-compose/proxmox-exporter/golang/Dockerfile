# --- Stage 1: Build ---
FROM golang:1.25-alpine AS builder

# Install git (required for fetching some Go dependencies)
RUN apk add --no-cache git

# Set the working directory
WORKDIR /app

# Copy dependency files first (optimizes Docker caching)
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the binary
# CGO_ENABLED=0 makes the binary statically linked (runs anywhere)
RUN CGO_ENABLED=0 GOOS=linux go build -o proxmox-exporter .

# --- Stage 2: Run ---
FROM alpine:latest

# Install CA certificates for secure HTTPS calls to Proxmox
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy only the compiled binary from the builder stage
COPY --from=builder /app/proxmox-exporter .

# Expose the default Prometheus exporter port
EXPOSE 9100

# Run the binary
CMD ["./proxmox-exporter"]