package cmd

import (
	"fmt"
	"os"
	"strconv"

	"github.com/spf13/cobra"
)

var deleteCmd = &cobra.Command{
	Use:   "delete <id>",
	Short: "Delete an expense",
	Args:  cobra.ExactArgs(1),
	Run: func(_ *cobra.Command, args []string) {
		c := newClient()
		id, err := strconv.Atoi(args[0])
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: invalid id %q\n", args[0])
			os.Exit(1)
		}
		if err := c.DeleteExpense(id); err != nil {
			fmt.Fprintf(os.Stderr, "error: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Expense %d deleted.\n", id)
	},
}
