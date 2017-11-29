package cmd

import (
	"fmt"
	"io/ioutil"
	"encoding/json"
	"github.com/peersafe/fabtest/tpl"
)

func CreateCert() error {
	obj := NewFabCmd("apply_cert.py", "")
	err := obj.RunShow("generate_certs", BinPath(), ConfigDir(), ConfigDir())
	if err != nil {
		return err
	}
	return nil
}


func CreateYamlByJson(strType string) error{
	var inputData map[string]interface{}
	var jsonData []byte
	var err error

	inputfile := InputDir() + strType + ".json"
	jsonData, err = ioutil.ReadFile(inputfile)
	if err != nil {
		return err
	}

	err = json.Unmarshal(jsonData, &inputData)
	if err != nil {
		return err
	}

	if strType == "configtx" {
		return tpl.Handler(inputData, TplConfigtx, ConfigDir()+"configtx.yaml")
	} else if strType == "crypto-config" {
		return tpl.Handler(inputData, TplCryptoConfig, ConfigDir()+"crypto-config.yaml")
	} else if strType == "node" {
		peerdomain := inputData[PeerDomain].(string)
		kfkdomain := inputData[KfkDomain].(string)
		list := inputData[List].([]interface{})
		for _, param := range list {
			value := param.(map[string]interface{})
			value[PeerDomain] = peerdomain
			value[KfkDomain] = kfkdomain
			nodeType := value[NodeType].(string)
			dir := ConfigDir()
			var outfile, tplfile, yamlname string
			switch nodeType {
			case TypeZookeeper:
				yamlname = nodeType + value[ZkId].(string) + value[Zk2Id].(string)
				tplfile = TplZookeeper
			case TypeKafka:
				yamlname = nodeType + value[KfkId].(string)
				tplfile = TplKafka
			case TypeOrder:
				yamlname = nodeType + value[OrderId].(string) + "org" + value[OrgId].(string)
				tplfile = TplOrderer
			case TypePeer:
				yamlname = nodeType + value[PeerId].(string) + "org" + value[OrgId].(string)
				tplfile = TplPeer
			}
			//生成yaml文件
			outfile = dir + yamlname
			err := tpl.Handler(value, tplfile, outfile + ".yaml")
			if err != nil {
				fmt.Errorf(err.Error())
			}
		}
	} else {
		return fmt.Errorf("%s not exist",strType)
	}
	return nil
}

func CreateGenesisBlock() error {
	obj := NewFabCmd("apply_cert.py", "")
	err := obj.RunShow("generate_genesis_block", BinPath(), ConfigDir(), ConfigDir())
	if err != nil {
		return err
	}
	return nil
}

func CreateChannelAnchorPeers(channelName string) error {
	obj := NewFabCmd("create_channel.py", "")
	err := obj.RunShow("create_channel", BinPath(), ConfigDir(), ChannelPath(), channelName, Domain_Name)
	if err != nil {
		return err
	}
	return nil
}

