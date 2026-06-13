package pluto

import (
	"encoding/json"
	"os"
)

type Config struct {
	Server string `json:"server"`
}

func DefaultConfigPath() string {
	return "config.json"
}

func LoadConfig(path string) (*Config, error) {
	cfg := &Config{Server: "http://localhost:8765"}
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return cfg, nil
		}
		return nil, err
	}
	if err := json.Unmarshal(data, cfg); err != nil {
		return nil, err
	}
	if v := os.Getenv("PLUTO_SERVER"); v != "" {
		cfg.Server = v
	}
	return cfg, nil
}
