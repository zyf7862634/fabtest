#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import local,lcd,cd,run,put,settings
import os
import utils
import string
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def generate_genesis_block(network_name):
    tool = utils.get_bin_path("configtxgen")
    outPath = utils.get_config_path(network_name, "channel-artifacts")
    env = "FABRIC_CFG_PATH=%s"%utils.get_config_path(network_name, "")
    local("mkdir -p %s"%outPath)
    local("%s %s -profile OrgsOrdererGenesis -outputBlock %s/genesis.block"%(env,tool,outPath))

#remote copy
def remote_copy(network_name,type):
    with lcd(utils.get_config_path(network_name, "")):
        local("tar -zcvf %s.tar.gz %s"%(type,type))
        put("%s.tar.gz"%type,"~/networklist/%s"%network_name)
        local("rm %s.tar.gz"%type)

    #remote
    with cd("~/networklist/%s"%network_name):
        run("tar zxvfm %s.tar.gz"%type)
        run("rm %s.tar.gz"%type)

## Generates orderer Org certs using cryptogen tool
def generate_orderder_certs(network_name, order_domain, order_uuid):
    cryptotool = utils.get_bin_path("cryptogen")
    yamlfile = utils.get_config_path(network_name, "docker-compose") + "/%s-crypto-config.yaml" % order_uuid
    outPath = utils.get_config_path(network_name, "crypto-config")

    local("%s generate --config=%s --output='%s'"%(cryptotool,yamlfile,outPath))
    with lcd(outPath + "/ordererOrganizations"):
        local("tar -zcvf %s.tar.gz %s" % (order_uuid, order_uuid))
        with settings(warn_only=True):
            run("mkdir -p ~/networklist/%s/crypto-config/ordererOrganizations"%network_name)
        put("%s.tar.gz"%order_uuid, "~/networklist/%s/crypto-config/ordererOrganizations"%network_name)
        local("rm %s.tar.gz"%order_uuid)
    #remote
    with cd("~/networklist/%s/crypto-config/ordererOrganizations"%network_name):
        run("tar zxvfm %s.tar.gz"%order_uuid)
        run("rm %s.tar.gz"%order_uuid)

def generate_peer_certs(network_name, org_name):
    cryptotool = utils.get_bin_path("cryptogen")
    yamlfile = utils.get_config_path(network_name, "docker-compose") + "/%s-crypto-config.yaml" % org_name
    outPath = utils.get_config_path(network_name, "crypto-config")

    local("%s generate --config=%s --output='%s'"%(cryptotool,yamlfile,outPath))
    with lcd(outPath + "/peerOrganizations"):
        local("tar -zcvf %s.tar.gz %s"%(org_name,org_name))
        with settings(warn_only=True):
            run("mkdir -p ~/networklist/%s/crypto-config/peerOrganizations"%network_name)
        put("%s.tar.gz"%org_name,"~/networklist/%s/crypto-config/peerOrganizations"%network_name)
        local("rm %s.tar.gz"%org_name)
    #remote
    with cd("~/networklist/%s/crypto-config/peerOrganizations"%network_name):
        run("tar zxvfm %s.tar.gz"%org_name)
        run("rm %s.tar.gz"%org_name)

def init_org_ca(network, org_name, ip, port, admin_name, admin_pwd):
    tool = utils.get_bin_path("fabric-ca-client")
    crypto_path = utils.get_config_path(network, "crypto-config")
    org_path = "%s/peerOrganizations/%s"%(crypto_path, org_name)
    admin_yaml = "%s/fabric-ca-admin-config.yaml"%org_path
    local("mkdir -p %s"%org_path)

    admin_dir = "%s/peerOrganizations/%s/Admin"%(crypto_path, org_name)
    admin_fact_dir = "%s/users/Admin@%s"%(org_path,org_name)
    admin_msp = "%s/msp"%admin_dir

    if os.path.exists(admin_msp+"/signcerts/cert.pem"):
        print "Admin is already enroll  orgname : %s"%org_path
        return

    local("rm -rf %s/*"%admin_msp)

    change_csr_config(utils.get_default_cfg_path(), admin_yaml, admin_name, org_name, ip, port)

    admin_enroll = "%s enroll -u http://%s:%s@%s:%s -c %s -M %s" \
                   %(tool,admin_name,admin_pwd,ip,port,admin_yaml,admin_msp)

    print "First enroll admin %s"%org_name
    local(admin_enroll)
    print "change admin cert name"
    #make org ca dir
    local("cp -r %s/cacerts %s/ca"%(admin_msp,org_path))
    with lcd("%s/ca"%org_path):
        temp_ip = string.replace(ip,'.','-')
        local("mv %s-%s.pem ca.%s-cert.pem" % (temp_ip, port, org_name))
    #make org tlsca dir
    local("cp -r %s/ca %s/tlsca"%(org_path,org_path))
    with lcd("%s/tlsca"%org_path):
        local("mv ca.%s-cert.pem tlsca.%s-cert.pem" % (org_name, org_name))
    #make admin@org dir
    change_cert_name(admin_fact_dir, "admin", org_name, "Admin@%s"%org_name, ip, port, admin_dir, org_path)
    #put to remote
    with lcd("%s/peerOrganizations"%crypto_path):
        local("tar -zcvf %s.tar.gz %s"%(org_name,org_name))
        with settings(warn_only=True):
            run("mkdir -p ~/networklist/%s/crypto-config/peerOrganizations"%network)
        put("%s.tar.gz"%org_name,"~/networklist/%s/crypto-config/peerOrganizations"%network)
        local("rm %s.tar.gz"%org_name)
    #remote
    with cd("~/networklist/%s/crypto-config/peerOrganizations"%network):
        run("tar zxvfm %s.tar.gz"%org_name)
        run("rm %s.tar.gz"%org_name)

def generate_certs_to_ca(network, org_name, full_name, pwd, ip, port, type, admin_name, admin_pwd):
    tool = utils.get_bin_path("fabric-ca-client")
    path = utils.get_config_path(network, "crypto-config")
    org_path = "%s/peerOrganizations/%s"%(path, org_name)
    client_yaml = "%s/fabric-ca-client-config.yaml"%org_path
    admin_yaml = "%s/fabric-ca-admin-config.yaml"%org_path

    admin_dir = "%s/peerOrganizations/%s/Admin"%(path, org_name)
    admin_fact_dir = "%s/users/Admin@%s"%(org_path,org_name)
    admin_msp = "%s/msp"%admin_dir
    if os.path.exists(admin_msp+"/signcerts/cert.pem") == False:
        init_org_ca(network, org_name, ip, port, admin_name, admin_pwd)
    cur_dir = "%s/peerOrganizations/%s/peers/%s"%(path, org_name, full_name)
    if type == "user":
        cur_dir = "%s/peerOrganizations/%s/users/%s"%(path, org_name, full_name)

    client_msp = "%s/msp"%cur_dir

    if os.path.exists(client_msp+"/signcerts/cert.pem") == True:
        print "user or peer is already enrolled full_name : %s"%full_name
        return

    register_cmd = "%s register --id.name %s --id.secret %s " \
                   "--id.type %s --id.affiliation org1.department1 -c %s -M %s" \
                   %(tool, full_name, pwd, type, admin_yaml, admin_msp)
    print "register %s.%s"%(full_name, org_name)
    local(register_cmd)

    change_csr_config(utils.get_default_cfg_path(), client_yaml, full_name, org_name, ip, port)

    enroll_cmd = "%s enroll -u http://%s:%s@%s:%s -c %s -M %s" \
                 %(tool, full_name, pwd, ip, port, client_yaml, client_msp)

    print "enroll %s" % full_name
    local(enroll_cmd)

    print "change peer or user cert name"
    change_cert_name(cur_dir, type, org_name, full_name, ip, port, admin_fact_dir, org_path)
    #put to remote
    remote_path = "~/networklist/%s/crypto-config/peerOrganizations/%s/%ss"%(network,org_name,type)
    with lcd("%s/%ss"%(org_path,type)):
        local("tar -zcvf %s.tar.gz %s"%(full_name,full_name))
        with settings(warn_only=True):
            run("mkdir -p %s"%remote_path)
        put("%s.tar.gz"%full_name,remote_path)

        local("rm %s.tar.gz"%full_name)
    #remote
    with cd(remote_path):
        run("tar zxvfm %s.tar.gz"%full_name)
        run("rm %s.tar.gz"%full_name)

def change_csr_config(file_path,dest,cn,org,ip,port):
    local("cp %s/fabric-ca-client-config-template.yaml %s"%(file_path,dest))
    local("sed -i 's/CSR_CN_NAME/%s/g' %s"%(cn,dest))
    local("sed -i 's/CSR_ORG_NAME/%s/g' %s"%(org,dest))
    local("sed -i 's/CSR_HOST/%s/g' %s"%(cn,dest))
    local("sed -i 's/URL_IP/%s/g' %s"%(ip,dest))
    local("sed -i 's/URL_PORT/%s/g' %s"%(port,dest))

def change_cert_name(cur_dir, type, org, name, ip, port, admin_dir, org_path):
    ip = string.replace(ip,'.','-')
    if type == "admin":
        local("mkdir -p %s/users"%org_path)
        local("cp -r %s %s"%(admin_dir,cur_dir))
        type = "user"

    if type == "user":
        local("cp -r %s/tlsca %s/msp/tlscacerts"%(org_path,cur_dir))
        with lcd("%s/msp/cacerts/"%cur_dir):
            local("mv %s-%s.pem ca.%s-cert.pem"%(ip,port,org))
        with lcd("%s/msp/signcerts/"%cur_dir):
            local("mv cert.pem %s-cert.pem"%name)
        with lcd("%s/msp"%cur_dir):
            local("cp -r signcerts admincerts")
        ##when admin
        if os.path.exists("%s/msp"%org_path) == False:
            local("cp -r %s/msp %s"%(cur_dir,org_path))
            with lcd(org_path):
                local("rm -r msp/signcerts")
                local("rm -r msp/keystore")

    elif type == "peer":
        local("cp -r %s/msp/admincerts %s/msp"%(admin_dir,cur_dir))
        local("cp -r %s/tlsca %s/msp/tlscacerts"%(org_path,cur_dir))
        with lcd("%s/msp/cacerts/"%cur_dir):
            local("mv %s-%s.pem ca.%s-cert.pem"%(ip,port,org))
        with lcd("%s/msp/signcerts/"%cur_dir):
            local("mv cert.pem %s-cert.pem"%name)

    #make tls dir
    local("mkdir -p %s/tls"%cur_dir)
    with lcd("%s/tls"%cur_dir):
        local("cp %s/msp/cacerts/ca.%s-cert.pem ca.crt"%(cur_dir,org))
        local("cp %s/msp/signcerts/%s-cert.pem server.crt"%(cur_dir,name))
        local("cp %s/msp/keystore/*_sk server.key"%cur_dir)
