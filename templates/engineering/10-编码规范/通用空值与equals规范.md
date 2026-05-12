# 通用空值与equals规范

## 1. 目的

避免空指针异常，统一对象比较写法。

## 2. 推荐写法

```java
if (Objects.equals(entity.getStatus(), StatusEnum.CLOSE.getCode())) {
    // ...
}

if (Objects.equals(kdBusinessFlag, BusinessConst.TWO)) {
    // ...
}
```

## 3. 可接受写法

左侧确定不为 null 时，可以常量或枚举在左侧：

```java
if (StatusEnum.CLOSE.getCode().equals(entity.getStatus())) {
    // ...
}

items.stream()
    .filter(item -> BusinessConst.ONE.equals(item.getType()));
```

## 4. 禁止写法

```java
if (entity.getStatus().equals(StatusEnum.CLOSE.getCode())) {
    // ...
}

if (configValue.equals(BusinessConst.TWO)) {
    // ...
}
```

## 5. 审查检查点

| 规则 ID | 检查内容 |
|---------|----------|
| NULL-001 | `.equals(` 左侧是否可能为 null。 |
| NULL-002 | `@Value` 注入字段是否直接调用 equals。 |
| NULL-003 | getter 返回值是否直接调用 equals。 |
| NULL-004 | 远程调用或数据库查询结果字段是否直接调用 equals。 |

