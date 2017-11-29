#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import local
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

## create channel

def create_channel(bin_path, yaml_path, out_path, channel_name, domain_name):
    if not os.path.exists(yaml_path + "core.yaml"):
        local("cp %s/core.yaml %s"%(bin_path, yaml_path))
    ret = create_channeltx(bin_path, yaml_path, out_path, channel_name)
    print ret
    channeltx_name = channel_name + '.tx'
    msp_path = yaml_path + "crypto-config/peerOrganizations/org1.%s/users/Admin@org1.%s/msp"%(domain_name,domain_name)
    channel_dir = out_path + channel_name
    order_tls_path = yaml_path +  "crypto-config/ordererOrganizations/ord1.%s/orderers/orderer0.ord1.%s/msp/tlscacerts/tlsca.ord1.%s-cert.pem"%(domain_name,domain_name,domain_name)
    env = 'FABRIC_CFG_PATH=%s '%yaml_path
    env = env + 'CORE_PEER_LOCALMSPID=\"org1MSP\" '
    env = env + ' CORE_PEER_MSPCONFIGPATH=%s  '%msp_path
    bin = bin_path + "peer"
    order_address = "orderer0.ord1.finblockchain.cn:7050"
    param = ' channel create -o %s -t 3000 -c %s -f %s/%s'%(order_address, channel_name, channel_dir, channeltx_name)

    tls = ' --tls --cafile %s'%order_tls_path

    command = env + bin + param + tls
    local(command)

def create_channeltx(bin_path, yaml_path, out_path, channel_name):
    bin = bin_path + "configtxgen"
    channel_dir = out_path + channel_name
    if not os.path.exists(channel_dir):
        local("mkdir -p %s"%channel_dir)
    channeltx_name = channel_name + '.tx'
    env = 'FABRIC_CFG_PATH=%s '%yaml_path
    param = ' -profile OrgsChannel -outputCreateChannelTx %s/%s -channelID %s'%(channel_dir, channeltx_name, channel_name)
    
    command = env + bin + param
    return local(command)
#
# def update_anchor(network_name, msp_id, order_domain, order_uuid, order_address, channel_name, org_name):
#     msp_path = utils.get_peer_msp_path(network_name, org_name)
#     channel_dir = utils.get_channel_path(network_name, channel_name)
#     order_tls_path = utils.get_order_tls_path(network_name, order_domain, order_uuid)
#
#     create_anchor_tx(network_name, channel_name, msp_id, msp_path)
#
#     env = ' FABRIC_CFG_PATH=%s '%utils.get_config_path(network_name,"")
#     env = env + ' CORE_PEER_LOCALMSPID=%s'%msp_id
#     env = env + ' CORE_PEER_MSPCONFIGPATH=%s'%msp_path
#     bin = utils.get_bin_path("peer")
#     param = ' channel update -o %s -c %s -f %s/%s%sanchors.tx'%(order_address, channel_name, channel_dir, msp_id, channel_name)
#     tls = ' --tls --cafile %s'%order_tls_path
#
#     command = env + bin + param + tls
#     return local(command)
#
# def create_anchor_tx(network_name, channel_name, msp_id, msp_path):
#     channel_dir = utils.get_channel_path(network_name, channel_name)
#     env = ' FABRIC_CFG_PATH=%s '%utils.get_config_path(network_name,"")
#     env = env + ' CORE_PEER_MSPCONFIGPATH=%s '%msp_path
#     param = ' -profile OrgsChannel -outputAnchorPeersUpdate %s/%s%sanchors.tx -channelID %s -asOrg %s'%(channel_dir, msp_id, channel_name, channel_name, msp_id)
#
#     bin = utils.get_bin_path("configtxgen")
#     command = env + bin + param
#     return local(command)
