package cmd

import "strconv"

func atoi(s string) int {
	n, err := strconv.Atoi(s)
	if err != nil {
		return 0
	}
	return n
}
