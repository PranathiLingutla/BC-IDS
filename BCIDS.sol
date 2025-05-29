// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract IPBlacklist {
    struct IP {
        bytes32 sourceIP;
        bytes32 destinationIP;
    }

    mapping(bytes32 => bool) public ipExists;
    IP[] public blackList;

    function batchUpdateIpList(bytes32[] memory _sourceIPs, bytes32[] memory _destinationIPs) public {
        require(_sourceIPs.length == _destinationIPs.length, "Mismatched array lengths");

        for (uint i = 0; i < _sourceIPs.length; i++) {
            bytes32 ipHash = keccak256(abi.encodePacked(_sourceIPs[i], _destinationIPs[i]));
            if (!ipExists[ipHash]) {
                ipExists[ipHash] = true;
                blackList.push(IP(_sourceIPs[i], _destinationIPs[i]));
            }
        }
    }

    function getIpList() public view returns (IP[] memory) {
        return blackList;
    }

    function getTotalEntries() public view returns (uint) {
        return blackList.length;
    }

    function getIp(uint index) public view returns (bytes32, bytes32) {
        require(index < blackList.length, "Index out of bounds");
        return (blackList[index].sourceIP, blackList[index].destinationIP);
    }
}
