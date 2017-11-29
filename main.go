package main

import (
	"flag"
	"fmt"
	"os"
	"github.com/peersafe/fabtest/cmd"
)

var (
	file = flag.String("f", "", "configtx, crypto-config, node")
	start = flag.String("s", "", "peer, order, zookeeper, kafka, all")
	image = flag.String("i", "", "peer, order, zookeeper, kafka, all")
	create = flag.String("c", "", "crypto, genesisblock, channel")
	channelname = flag.String("n", "", "channelname")
)

func main() {
	flag.Parse()
	var err error
	if *file != "" {
		err = cmd.CreateYamlByJson(*file)
	}else if *start != "" {
		err = cmd.StartNode(*start)
	}else if *image != ""{
		err = cmd.LoadImage(*image)
	}else if *create == "genesisblock"{
		err = cmd.CreateGenesisBlock()
	}else if *create == "crypto"{
		err = cmd.CreateCert()
	}else if *create == "channel"{
		if *channelname == ""{
			flag.Usage()
			fmt.Println("channel name is nil")
			os.Exit(1)
		}
		err = cmd.CreateChannelAnchorPeers(*channelname)
	}else {
		fmt.Println("Both data and file are nil.")
		flag.Usage()
		os.Exit(1)
	}
	if err != nil {
		fmt.Println(err)
	}
}
