# eth_simulateV1 Proxy Service

Это рабочее решение для предоставления `eth_simulateV1` RPC метода, используя `eth_call` из op-geth.

## Что это?

Прокси-сервис на Python/Flask, который:
1. Принимает `eth_simulateV1` RPC запросы
2. Преобразует их в `eth_call` и `eth_estimateGas`
3. Отправляет в op-geth backend
4. Возвращает результаты в формате `eth_simulateV1`

## Архитектура

```
┌─────────────────┐
│   Клиент /     │
│   Тесты        │
└────────┬────────┘
         │ eth_simulateV1
         ▼
┌─────────────────┐
│  Прокси сервис  │  ← eth_simulate_proxy/proxy_service.py
│  (Python)      │
│  Порт: 28545   │
└────────┬────────┘
         │ eth_call, eth_estimateGas
         ▼
┌─────────────────┐
│   op-geth       │  ← ghcr.io/unitsnetwork/op-geth:v1.101603.0-1
│   Порт: 18545   │
└─────────────────┘
```

## Быстрый старт

### 1. Сгенерировать конфигурацию

```bash
cd /home/engine/project/eth_simulate_proxy
chmod +x setup_config.sh
./setup_config.sh
```

### 2. Запустить сеть

```bash
cd /home/engine/project
docker-compose -f docker-compose.eth-simulate.yml up -d
```

### 3. Проверить статус

```bash
# Проверить контейнеры
docker ps

# Проверить логи
docker logs ec-1 --tail 20
docker logs ec-2 --tail 20

# Проверить здоровье
curl http://127.0.0.1:28545/health
```

### 4. Протестировать eth_simulateV1

```bash
curl -X POST http://127.0.0.1:28545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "eth_simulateV1",
    "params": [
      [{
        "from": "0x7dbcf9c6c3583b76669100f9be3caf6d722bc9f9",
        "to": "0x7dbcf9c6c3583b76669100f9be3caf6d722bc9f9",
        "value": "0x0",
        "data": "0x"
      }],
      "latest"
    ],
    "id": 1
  }'
```

## API Эндпоинты

### RPC API (Port 28545)

#### eth_simulateV1

```bash
POST /
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "eth_simulateV1",
  "params": [
    [
      {
        "from": "0x...",
        "to": "0x...",
        "value": "0x...",
        "data": "0x...",
        "gas": "0x..."
      }
    ],
    "latest"  // или hex номер блока
  ],
  "id": 1
}
```

**Ответ:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "gasUsed": "0x5208",
      "logs": [],
      "output": "0x",
      "returnData": "0x",
      "status": "0x1",
      "accountAccesses": [],
      "logsBloom": "0x00000000..."
    }
  ]
}
```

#### Другие методы

Все стандартные Ethereum RPC методы проксируются в op-geth:
- `eth_blockNumber`
- `eth_getBalance`
- `eth_call`
- и т.д.

### Health Checks

```bash
GET /health
# Возвращает: {"status": "healthy", "backend": "connected", "latest_block": "0x..."}
```

```bash
GET /ready
# Возвращает: {"ready": true}
```

## Структура проекта

```
eth_simulate_proxy/
├── proxy_service.py      # Flask приложение (прокси сервис)
├── Dockerfile           # Dockerfile для сборки образа
├── requirements.txt     # Python зависимости
├── setup_config.sh      # Генерация конфигураций
└── configs/
    ├── config.toml      # Конфигурация op-geth
    ├── genesis.json      # Genesis блок
    ├── jwtsecret.hex    # JWT секрет
    └── p2p-key-*.hex  # P2P ключи
```

## Файлы

### proxy_service.py

Flask приложение, которое:
1. Принимает RPC запросы
2. Если это `eth_simulateV1` - обрабатывает особенным образом
3. Иначе - проксирует в backend (op-geth)

### Dockerfile

Создает lightweight Python контейнер с Flask и зависимостями.

### requirements.txt

Зависимости Python:
- Flask 3.0.0
- Flask-CORS 4.0.0
- Web3.py 6.11.3
- eth-account 0.9.0
- requests 2.31.0

## Docker Compose

Файл: `/home/engine/project/docker-compose.eth-simulate.yml`

### Сервисы

#### ec-1 (op-geth)
- Образ: `ghcr.io/unitsnetwork/op-geth:v1.101603.0-1`
- Порты: 18545 (HTTP), 18546 (WS), 18551 (Engine)
- Майнит блоки автоматически
- Служит backend для прокси

#### ec-2 (proxy service)
- Собирается из `eth_simulate_proxy/Dockerfile`
- Порты: 28545 (HTTP), 28546 (WS)
- Подключается к ec-1 как backend
- Предоставляет `eth_simulateV1` endpoint

## Тестирование

### Автоматические тесты

```bash
# Использовать тестовые скрипты из проекта
cd /home/engine/project

# Запустить тесты
python3 tests/test_eth_simulate.py

# Быстрый тест
python3 tests/quick_test.py --client proxy
```

### Ручное тестирование

```bash
# 1. Простой вызов
curl -X POST http://127.0.0.1:28545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"eth_simulateV1",
    "params":[[{
      "from":"0x7dbcf9c6c3583b76669100f9be3caf6d722bc9f9",
      "to":"0x7dbcf9c6c3583b76669100f9be3caf6d722bc9f9",
      "value":"0x0",
      "data":"0x"
    }], "latest"],
    "id":1
  }'

# 2. Симуляция перевода
curl -X POST http://127.0.0.1:28545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"eth_simulateV1",
    "params":[[{
      "from":"0x7dbcf9c6c3583b76669100f9be3caf6d722bc9f9",
      "to":"0xa50a51c09a5c451C52BB714527E1974b686D8e77",
      "value":"0xde0b6b3a7640000",
      "data":"0x"
    }], "latest"],
    "id":1
  }'

# 3. Симуляция нескольких транзакций
curl -X POST http://127.0.0.1:28545 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"eth_simulateV1",
    "params":[[
      {
        "from":"0x7dbcf9c6c3583b76669100f9be3caf6d722bc9f9",
        "to":"0xa50a51c09a5c451C52BB714527E1974b686D8e77",
        "value":"0xde0b6b3a7640000",
        "data":"0x"
      },
      {
        "from":"0x7dbcf9c6c3583b76669100f9be3caf6d722bc9f9",
        "to":"0x9a3DBCa554e9f6b9257aAa24010DA8377C57c17e",
        "value":"0xbc614e0000",
        "data":"0x"
      }
    ], "latest"],
    "id":1
  }'
```

## Мониторинг

### Логи

```bash
# Логи прокси сервиса
docker logs ec-2 -f

# Логи op-geth
docker logs ec-1 -f

# Все логи
docker-compose -f docker-compose.eth-simulate.yml logs -f
```

### Статус

```bash
# Проверить здоровье
curl http://127.0.0.1:28545/health

# Проверить готовность
curl http://127.0.0.1:28545/ready

# Проверить состояние контейнеров
docker-compose -f docker-compose.eth-simulate.yml ps
```

## Остановка

```bash
# Остановить контейнеры
docker-compose -f docker-compose.eth-simulate.yml down

# Остановить и удалить volumes
docker-compose -f docker-compose.eth-simulate.yml down -v

# Удалить конфигурации
rm -rf eth_simulate_proxy/configs/*
```

## Troubleshooting

### Прокси не стартует

```bash
# Проверить логи
docker logs ec-2 --tail 50

# Проверить, что op-geth запущен
docker ps | grep ec-1

# Проверить конфигурацию
docker exec ec-1 cat /etc/config.toml
```

### eth_simulateV1 возвращает ошибку

```bash
# Проверить здоровье backend
curl http://127.0.0.1:28545/health

# Проверить, что op-geth отвечает напрямую
curl -X POST http://127.0.0.1:18545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### Контейнеры не могут соединиться

```bash
# Проверить сеть
docker network inspect eth-simulate-test_testnet

# Пинг с одного контейнера на другой
docker exec ec-2 ping ec-1
```

## Преимущества подхода

✅ **Простота**: Нет необходимости патчить Reth на Rust
✅ **Надежность**: Использует проверенный op-geth для симуляции
✅ **Гибкость**: Легко модифицировать Python код
✅ **Совместимость**: Работает с любым backend, поддерживающим eth_call
✅ **Быстрая разработка**: Реализовано за несколько часов вместо недель

## Ограничения

⚠️ **Logs**: Логи транзакций могут быть неполными (требует trace_transaction)
⚠️ **Deposit transactions**: Требуется специальная обработка для OP Stack
⚠️ **Performance**: Прокси добавляет overhead (обычно минимальный)
⚠️ **State access**: Полная информация о доступе к состоянию не доступна

## Дополнительные ресурсы

- [Спецификация eth_simulateV1](https://github.com/ethereum/execution-apis/blob/main/src/eth/simulation.yaml)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)

## Лицензия

MIT
