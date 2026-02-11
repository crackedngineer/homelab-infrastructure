package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"context"

	"github.com/luthermonson/go-proxmox"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// 1. Define the structure of your metric
var lxcIpDesc = prometheus.NewDesc(
	"proxmox_lxc_network_info",
	"IP address information for Proxmox LXC containers",
	[]string{"name", "vmid", "ip"}, // Labels
	nil,
)

// 2. Define the Exporter struct
type ProxmoxExporter struct {
	proxmox *proxmox.Client
}

// Simulated API Fetcher
type ContainerInfo struct {
	Name string
	VMID string
	IP   string
	// NetIface string
}

// 3. Implement the Describe method (required by prometheus.Collector)
func (e *ProxmoxExporter) Describe(ch chan<- *prometheus.Desc) {
	ch <- lxcIpDesc
}

func (e *ProxmoxExporter) fetchLxcData(ctx context.Context) ([]ContainerInfo, error) {
	nodes, err := e.proxmox.Nodes(ctx)
	if err != nil {
		return nil, err
	}

	var lxc []ContainerInfo
	for _, node := range nodes {
		resNode, err := e.proxmox.Node(ctx, node.Node)
		if err != nil {
			return nil, err
		}
		containers, err := resNode.Containers(ctx)
		if err != nil {
			return nil, err
		}
		for _, container := range containers {
			interfaces, err := container.Interfaces(ctx)
			if err != nil {
				return nil, err
			}
			ipAddr := strings.Split(interfaces[1].Inet, "/")[0]
			lxc = append(lxc, ContainerInfo{
				Name: container.Name,
				VMID: fmt.Sprintf("%d", container.VMID),
				IP:   ipAddr,
			})
		}
	}
	// Placeholder: return empty slice for now
	return lxc, nil
}

// 4. The Collect method: This is where the magic happens
func (e *ProxmoxExporter) Collect(ch chan<- prometheus.Metric) {
	// In a real app, you'd fetch from Proxmox here.
	// For this tutorial, we'll simulate the API call logic.
	ctx := context.Background()
	containers, err := e.fetchLxcData(ctx)
	if err != nil {
		log.Printf("Error fetching data: %v", err)
		return
	}

	for _, c := range containers {
		// We use GaugeValue with 1 to indicate the 'existence' of this IP mapping
		ch <- prometheus.MustNewConstMetric(
			lxcIpDesc,
			prometheus.GaugeValue,
			1,
			c.Name, c.VMID, c.IP,
		)
	}
}

func NewProxmoxExporter(apiURL string, username string, password string) *ProxmoxExporter {
	insecureHTTPClient := http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{
				InsecureSkipVerify: true,
			},
		},
	}

	credentials := proxmox.Credentials{
		Username: username,
		Password: password,
	}

	client := proxmox.NewClient(apiURL,
		proxmox.WithHTTPClient(&insecureHTTPClient),
		proxmox.WithCredentials(&credentials),
	)

	version, err := client.Version(context.Background())
	if err != nil {
		panic(err)
	}
	fmt.Println(version.Release) // 7.4
	if client == nil {
		log.Printf("Error creating Proxmox client")
		return nil
	}
	return &ProxmoxExporter{
		proxmox: client,
	}
}

func main() {
	HOST := os.Getenv("PROXMOX_HOST")
	USERNAME := os.Getenv("PROXMOX_USER")
	PASSWORD := os.Getenv("PROXMOX_PASSWORD")
	PORT := os.Getenv("EXPORTER_PORT")
	if PORT == "" {
		PORT = "9100"
	}

	if HOST == "" || USERNAME == "" || PASSWORD == "" {
		log.Fatal("Please set PROXMOX_HOST, PROXMOX_USER, and PROXMOX_PASSWORD environment variables")
	}

	exporter := NewProxmoxExporter(
		fmt.Sprintf("https://%s:8006/api2/json", HOST),
		USERNAME,
		PASSWORD,
	)

	// Register the exporter
	prometheus.MustRegister(exporter)

	// Serve the metrics
	http.Handle("/metrics", promhttp.Handler())
	fmt.Println("Exporter running on :" + PORT + "/metrics")
	log.Fatal(http.ListenAndServe(":"+PORT, nil))
}
