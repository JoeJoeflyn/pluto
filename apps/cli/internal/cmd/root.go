package cmd

import (
	"fmt"
	"os"

	pluto "github.com/giogio/pluto/cli/internal"
	"github.com/spf13/cobra"
)

var (
	serverFlag string
	client     *pluto.Client
)

func newClient() *pluto.Client {
	if client != nil {
		return client
	}
	cfg, err := pluto.LoadConfig(pluto.DefaultConfigPath())
	if err != nil {
		fmt.Fprintf(os.Stderr, "warning: config: %v\n", err)
		cfg = &pluto.Config{Server: "http://localhost:8765"}
	}
	if serverFlag != "" {
		cfg.Server = serverFlag
	}
	client = pluto.NewClient(cfg.Server)
	return client
}

var RootCmd = &cobra.Command{
	Use:   "pluto",
	Short: "Local-first AI receipt scanner",
	Long: `Pluto scans receipts using a local AI model and tracks your spending.
Point it at the Pluto API server (default http://localhost:8765).`,
}

func Execute() {
	if err := RootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func init() {
	RootCmd.PersistentFlags().StringVarP(&serverFlag, "server", "s", "", "Pluto API server URL (overrides config.json and PLUTO_SERVER env)")
	RootCmd.AddCommand(listCmd)
	RootCmd.AddCommand(getCmd)
	RootCmd.AddCommand(deleteCmd)
	RootCmd.AddCommand(statsCmd)
	RootCmd.AddCommand(scanCmd)
	RootCmd.AddCommand(categoriesCmd)
	RootCmd.AddCommand(merchantsCmd)
	RootCmd.AddCommand(healthCmd)
}
