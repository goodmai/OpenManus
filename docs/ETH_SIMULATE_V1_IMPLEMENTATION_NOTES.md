# Документация: eth_simulateV1 Patch для Reth

## Важно

Этот патч и Dockerfile - это **только структура** для демонстрации подхода.
Для реальной работы нужна фактическая имплементация eth_simulateV1 на Rust.

## Что нужно для полной реализации:

### 1. Rust Implementation

В `crates/rpc/rpc/src/eth.rs` нужно добавить метод:

```rust
pub fn eth_simulate_v1(
    transactions: Vec<TxEnvelope>,
    block_number_or_hash: BlockId,
) -> Result<Vec<SimulationResult>> {
    // 1. Получить состояние блока
    let state = get_state(block_number_or_hash)?;

    // 2. Создать временную среду для симуляции
    let mut env = create_env(state.clone());

    // 3. Симулировать каждую транзакцию
    let results = transactions
        .into_iter()
        .map(|tx| simulate_transaction(&mut env, tx))
        .collect::<Result<Vec<_>>>()?;

    Ok(results)
}

fn simulate_transaction(
    env: &mut EvmEnv,
    tx: TxEnvelope,
) -> Result<SimulationResult> {
    // Выполнить транзакцию
    let exec_result = env.transact(tx)?;

    Ok(SimulationResult {
        gas_used: exec_result.gas_used,
        logs: exec_result.logs,
        output: exec_result.output,
        return_data: exec_result.return_data,
        status: exec_result.status,
        // ... другие поля
    })
}
```

### 2. Добавить в API

В `crates/rpc/rpc-types/src/eth.rs`:

```rust
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, Eq)]
pub struct SimulationResult {
    pub gas_used: U256,
    pub logs: Vec<Log>,
    pub output: Bytes,
    pub return_data: Bytes,
    pub status: U64,
    pub account_accesses: Option<Vec<AccountAccess>>,
    // ... другие поля согласно спецификации
}
```

### 3. Зарегистрировать RPC метод

В `crates/rpc/rpc/src/lib.rs`:

```rust
impl EthApiServer for EthImpl {
    // ... другие методы

    async fn simulate_v1(
        &self,
        transactions: Vec<TxEnvelope>,
        block_id: BlockId,
    ) -> RpcResult<Vec<SimulationResult>> {
        self.eth_simulate_v1(transactions, block_id)
            .await
            .map_err(Into::into)
    }
}
```

### 4. Оптимизация для OP Stack

Для работы с OP Stack нужно учесть:
- Optimism-specific transaction envelopes
- L1 fee computation
- Bedrock transaction types
- Deposit transaction simulation

## Спецификация eth_simulateV1

Согласно [execution-apis](https://github.com/ethereum/execution-apis/blob/main/src/eth/simulation.yaml):

```yaml
method: eth_simulateV1
params:
  - name: transactions
    type: array[Transaction]
  - name: block_number_or_hash
    type: BlockIdentifier
result:
  name: SimulationResults
  type: array[SimulationResult]
```

## Текущее состояние

### Что создано:
✅ Dockerfile.op-reth-simulate - структура для сборки
✅ patches/eth_simulateV1.patch - заглушка для патча
✅ Конфигурация Docker Compose для использования модифицированного образа

### Что НЕ реализовано:
❌ Фактическая Rust имплементация eth_simulateV1
❌ Интеграция с OP Stack (optimism-specific features)
❌ Симуляция deposit транзакций
❌ Тесты имплементации

## Альтернативный подход

Вместо патчинга Reth можно:

1. **Использовать существующий reth с eth_simulateV1**:
   - Проверить, есть ли уже в последних версиях
   - Если да - использовать его напрямую

2. **Написать отдельный сервис**:
   - Python/Go сервис для симуляции
   - Использовать reth как data source
   - Реализовать eth_simulateV1 в этом сервисе

3. **Использовать другой клиент**:
   - Nethermind или Erigon с поддержкой eth_simulateV1
   - Как execution client в сети

## Рекомендация

Для текущей задачи рекомендуется:

1. Проверить, есть ли eth_simulateV1 в официальном reth
2. Если нет - создать issue/request для добавления
3. Временно использовать альтернативный подход или стандартный geth с eth_call

## Ссылки

- [Reth Repository](https://github.com/paradigmxyz/reth)
- [eth_simulateV1 Spec](https://github.com/ethereum/execution-apis/blob/main/src/eth/simulation.yaml)
- [OP Stack Documentation](https://docs.optimism.io/stack/protocol)
- [Optimism Repository](https://github.com/ethereum-optimism/optimism)
