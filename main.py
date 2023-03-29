import os
import time
import json
from web3 import Web3, HTTPProvider
from eth_account import Account

# Замените на свой API-ключ Alchemy и желаемое ENS-имя
ALCHEMY_API_KEY = 'your_alchemy_api_key'
ENS_NAME = 'yourdesiredname.eth'  # Замените на желаемое ENS-имя

# Подключение к сети Ethereum
w3 = Web3(HTTPProvider(f'https://eth-mainnet.alchemyapi.io/v2/{ALCHEMY_API_KEY}'))

# Загрузка закрытых ключей из файла
with open('private_keys.txt', 'r') as f:
    private_keys = f.read().splitlines()

# Загрузка ABI ENS Registrar из файла
with open('ens_registrar_abi.json', 'r') as f:
    ENS_REGISTRAR_ABI = json.load(f)

# Загрузка ABI ENS Public Resolver из файла
with open('ens_public_resolver_abi.json', 'r') as f:
    ENS_PUBLIC_RESOLVER_ABI = json.load(f)

# Установка адресов ENS Registrar и ENS Public Resolver
ENS_REGISTRAR_ADDRESS = '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e'
ENS_PUBLIC_RESOLVER_ADDRESS = '0x4976fb03C32e5B8cfe2b6cCB31c09Ba78EBaBa41'

# Инициализация контрактов
ens_registrar_contract = w3.eth.contract(
    address=ENS_REGISTRAR_ADDRESS, abi=ENS_REGISTRAR_ABI)
ens_public_resolver_contract = w3.eth.contract(
    address=ENS_PUBLIC_RESOLVER_ADDRESS, abi=ENS_PUBLIC_RESOLVER_ABI)

# Установка хэша ENS-имени
namehash = Web3.sha3(text=ENS_NAME)

for private_key in private_keys:
    # Получение аккаунта из закрытого ключа
    account = Account.from_key(private_key)
    nonce = w3.eth.getTransactionCount(account.address)

    # Оценка газа для регистрации домена
    gas_estimate = ens_registrar_contract.functions.register(
        namehash, account.address).estimateGas()

    # Подготовка транзакции
    transaction = ens_registrar_contract.functions.register(
        namehash, account.address).buildTransaction({
            'chainId': 1,  # Основная сеть Ethereum
            'gas': gas_estimate,
            'gasPrice': w3.toWei('30', 'gwei'),
            'nonce': nonce,
    })

    # Подписание транзакции
    signed_transaction = account.sign_transaction(transaction)

    # Отправка транзакции
    transaction_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

    # Ожидание майнинга транзакции
    transaction_receipt = w3.eth.waitForTransactionReceipt(transaction_hash)

    if transaction_receipt['status'] == 1:
        print(f"Домен '{ENS_NAME}' успешно зарегистрирован для {account.address}!")
    else:
        print(f"Не удалось зарегистрировать домен '{ENS_NAME}' для адреса {account.address}")
