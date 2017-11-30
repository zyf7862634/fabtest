logging:
    peer:       warning
    node:       warning
    network:    warning
    version:    warning
    protoutils: warning
    error:      warning
    msp:        critical

    format: '%{color}%{time:2006-01-02 15:04:05.000 MST} [%{module}] %{shortfunc} -> %{level:.4s} %{id:03x}%{color:reset} %{message}'

###############################################################################
#
#    client section
#
###############################################################################
client:
    tls:
      enabled: true
    peers:
        # peer0
        - address: "peer{{.peer_id}}.org{{.org_id}}.{{.peer_domain}}:7051"
          eventHost: "peer{{.peer_id}}.org{{.org_id}}.{{.peer_domain}}"
          eventPort: 7053
          primary: true
          localMspId: Org{{.org_id}}MSP
          tls:
              # Certificate location absolute path
              certificate: "./crypto-config/peerOrganizations/org{{.org_id}}.{{.peer_domain}}/peers/peer{{.peer_id}}.org{{.org_id}}.{{.peer_domain}}/tls/ca.crt"
              serverHostOverride: "peer{{.peer_id}}"

    orderer:
        - address: "orderer{{.peer_id}}.ord{{.org_id}}.{{.peer_domain}}:7050"
          tls:
            # Certificate location absolute path
            certificate: "./crypto-config/ordererOrganizations/ord{{.org_id}}.{{.peer_domain}}/orderers/orderer{{.peer_id}}.{{.org_id}}.{{.peer_domain}}/msp/tlscacerts/tlsca.ord{{.org_id}}.{{.peer_domain}}-cert.pem"
            serverHostOverride: "orderer{{.peer_id}}"

###############################################################################
#
#    Chaincode section
#
###############################################################################
chaincode:
    id:
        name: {{.ccname}}
        version: "{{.ccversion}}"
        chainID: {{.channelname}}

user:
    alias: zhengfu998

apiserver:
    listenport: {{.apiport}}
    probe_order: "orderer{{.peer_id}}.{{.org_id}}.{{.peer_domain}} 7050"
###############################################################################
#
#    other section
#
###############################################################################
other:
    mq_address:
      - "amqp://testpoc:123456@10.10.255.71:5672/"
      - "amqp://testpoc:123456@10.10.255.72:5672/"
    queue_name: "fftQueue"
    system_queue_name: "sys_fftQueue"
