package main

import (
	"encoding/json"
	"flag"
	"fmt"
	df "github.com/peersafe/fabtest/cmd"
	"github.com/peersafe/fabtest/tpl"
	"io/ioutil"
	"os"
)

var (
	file = flag.String("f", "", "configtx, crypto-config, node")
)

func main() {
	flag.Parse()

	if *file == "" {
		fmt.Println("Both data and file are nil.")
		flag.Usage()
		os.Exit(1)
	}

	var inputData map[string]interface{}
	var jsonData []byte
	var err error

	inputfile := df.InputDir + *file + ".json"
	jsonData, err = ioutil.ReadFile(inputfile)
	if err != nil {
		panic(err)
	}

	err = json.Unmarshal(jsonData, &inputData)
	if err != nil {
		panic(err)
	}

	if *file == "configtx" {
		tpl.Handler(inputData, df.TplConfigtx, df.OutDir+"configtx.yaml")
	} else if *file == "crypto-config" {
		tpl.Handler(inputData, df.TplCryptoConfig, df.OutDir+"crypto-config.yaml")
	} else if *file == "node" {
		peerdomain := inputData[df.PeerDomain].(string)
		kfkdomain := inputData[df.KfkDomain].(string)
		list := inputData[df.List].([]interface{})
		for _, param := range list {
			value := param.(map[string]interface{})
			value[df.PeerDomain] = peerdomain
			value[df.KfkDomain] = kfkdomain
			nodeType := value[df.NodeType].(string)
			dir := df.OutDir
			var nodeId, outfile, tplfile, yamlname string
			switch nodeType {
			case df.TypeZookeeper:
				nodeId = value[df.ZkId].(string) + value[df.Zk2Id].(string)
				yamlname = nodeType + value[df.ZkId].(string) + value[df.Zk2Id].(string)
				tplfile = df.TplZookeeper
			case df.TypeKafka:
				nodeId = value[df.KfkId].(string)
				yamlname = nodeType + value[df.KfkId].(string)
				tplfile = df.TplKafka
			case df.TypeOrder:
				nodeId = value[df.OrderId].(string)
				yamlname = nodeType + value[df.OrderId].(string) + "org" + value[df.OrgId].(string)
				tplfile = df.TplOrderer
			case df.TypePeer:
				nodeId = value[df.PeerId].(string)
				yamlname = nodeType + value[df.PeerId].(string) + "org" + value[df.OrgId].(string)
				tplfile = df.TplPeer
			}
			//生成yaml文件
			outfile = dir + yamlname
			err := tpl.Handler(value, tplfile, outfile + ".yaml")
			if err != nil {
				fmt.Errorf(err.Error())
			}
			//启动节点
			cmd := df.NewFabCmd("add_node.py", value[df.IP].(string))
			configDir := os.Getenv("PWD") + "/configYaml"
			err = cmd.RunShow("start_node", nodeType, nodeId, yamlname, configDir)
			if err != nil {
				fmt.Println(err.Error())
			}
		}
	} else {
		flag.Usage()
		os.Exit(1)
	}
}
