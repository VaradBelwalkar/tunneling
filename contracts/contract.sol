// SPDX-License-Identifier: MIT
// Implemeting user verification through Ownership of contract, so the event producing functions are only available to the contract owners

pragma solidity ^0.8.0;

abstract contract Context {
    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }

    function _msgData() internal view virtual returns (bytes calldata) {
        return msg.data;
    }
}


abstract contract Ownable is Context {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor() {
        _transferOwnership(_msgSender());
    }


    modifier onlyOwner() {
        _checkOwner();
        _;
    }


    function owner() public view virtual returns (address) {
        return _owner;
    }


    function _checkOwner() internal view virtual {
        require(owner() == _msgSender(), "Ownable: caller is not the owner");
    }

    function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }


    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(newOwner);
    }


    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}





contract Interoperability_Mechanism is Ownable {

    event get_request(string context,bytes bytesHTTPReq);
    event get_response(string context,bytes bytesHTTPRes);


    function request_handler(string memory context,bytes memory bytesHTTPReq) public onlyOwner {
        emit get_request(context,bytesHTTPReq);
    }

    
    function response_handler(string memory context,bytes memory bytesHTTPRes) public onlyOwner {
        emit get_response(context,bytesHTTPRes);
    }

}

