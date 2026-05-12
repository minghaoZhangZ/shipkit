# Spring事务与并发规范

## 1. 目的

约束 Spring 事务边界、锁顺序、外部调用和并发状态变更。

## 2. 事务规则

| 规则 ID | 规则 | 说明 |
|---------|------|------|
| TX-001 | 遵循小事务原则。 | 查询、计算、外部调用放到事务外，只把最终状态变更放入事务。 |
| TX-002 | 禁止事务内调用外部系统。 | 包括 WMS、SAP、HTTP、RPC、消息发送和慢 IO。 |
| TX-003 | 写操作事务边界放在 Service 层。 | 不在 Controller 或 Repository 拼装业务事务。 |
| TX-004 | 状态变更必须考虑幂等和非法状态流转。 | 幂等键检查应先于状态变更。 |

## 3. 锁与事务顺序

锁生命周期必须包含事务生命周期。方法内必须加锁时，避免直接使用 `@Transactional`，优先使用 `TransactionTemplate` 手动控制。

```java
lock.lock();
try {
    // 1. 校验逻辑
    transactionTemplate.execute(status -> {
        // 2. 数据库更新操作
        return null;
    });
} finally {
    if (lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

## 4. Self-review 映射

| 自查项 ID | 来源规则 | 检查内容 |
|-----------|----------|----------|
| SR-TX-001 | TX-002 | 事务内是否调用外部系统或慢 IO。 |
| SR-TX-002 | TX-004 | 状态变更是否有幂等和并发控制。 |

