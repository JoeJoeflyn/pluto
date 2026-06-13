package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var healthCmd = &cobra.Command{
	Use:   "health",
	Short: "Check server health",
	Run: func(_ *cobra.Command, _ []string) {
		c := newClient()
		status, err := c.Health()
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		fmt.Println(status)
	},
}
