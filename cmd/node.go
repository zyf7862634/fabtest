package cmd

import (
	"encoding/json"
	"fmt"
	"github.com/peersafe/fabtest/tpl"
	"io/ioutil"
)

func StartNode(stringType string) error {
	var inputData map[string]interface{}
	var jsonData []byte
	var err error

	inputfile := InputDir() + "node.json"
	jsonData, err = ioutil.ReadFile(inputfile)
	if err != nil {
		return err
	}

	err = json.Unmarshal(jsonData, &inputData)
	if err != nil {
		return err
	}

	peerdomain := inputData[PeerDomain].(string)
	kfkdomain := inputData[KfkDomain].(string)
	list := inputData[List].([]interface{})
	for _, param := range list {
		value := param.(map[string]interface{})
		value[PeerDomain] = peerdomain
		value[KfkDomain] = kfkdomain
		nodeType := value[NodeType].(string)
		if nodeType != stringType && stringType != "all"{
			continue
		}
		dir := ConfigDir()
		var nodeId, outfile, tplfile, yamlname string
		switch nodeType {
		case TypeZookeeper:
			nodeId = value[ZkId].(string) + value[Zk2Id].(string)
			yamlname = nodeType + value[ZkId].(string) + value[Zk2Id].(string)
			tplfile = TplZookeeper
		case TypeKafka:
			nodeId = value[KfkId].(string)
			yamlname = nodeType + value[KfkId].(string)
			tplfile = TplKafka
		case TypeOrder:
			nodeId = value[OrderId].(string)
			yamlname = nodeType + value[OrderId].(string) + "org" + value[OrgId].(string)
			tplfile = TplOrderer
		case TypePeer:
			nodeId = value[PeerId].(string)
			yamlname = nodeType + value[PeerId].(string) + "org" + value[OrgId].(string)
			tplfile = TplPeer
		}
		//生成yaml文件
		outfile = dir + yamlname
		err := tpl.Handler(value, tplfile, outfile+".yaml")
		if err != nil {
			fmt.Errorf(err.Error())
		}
		//启动节点
		obj := NewFabCmd("add_node.py", value[IP].(string))
		err = obj.RunShow("start_node", nodeType, nodeId, yamlname, ConfigDir())
		if err != nil {
			return err
		}
	}

	return nil
}

func LoadImage(stringType string) error {
	var inputData map[string]interface{}
	var jsonData []byte
	var err error

	inputfile := InputDir() + "node.json"
	jsonData, err = ioutil.ReadFile(inputfile)
	if err != nil {
		return err
	}

	err = json.Unmarshal(jsonData, &inputData)
	if err != nil {
		return err
	}

	if stringType == "all" {
		list := inputData[List].([]interface{})
		for _, param := range list {
			value := param.(map[string]interface{})
			nodeType := value[NodeType].(string)
			//copy images
			obj := NewFabCmd("add_node.py", value[IP].(string))
			err = obj.RunShow("load_images", nodeType, ImagePath())
			if err != nil {
				return err
			}
			if nodeType == TypePeer {
				err = obj.RunShow("load_images", "baseos", ImagePath())
				if err != nil {
					return err
				}
				err = obj.RunShow("load_images", "ccenv", ImagePath())
				if err != nil {
					return err
				}
			}
		}
	} else {
		return fmt.Errorf("%s not exist", stringType)
	}
	return nil
}
