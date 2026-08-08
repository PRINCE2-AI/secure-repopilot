# Division by zero should return None

The `divide(a, b)` helper currently raises `ZeroDivisionError` when `b` is `0`.

Expected behavior:

- `divide(8, 0)` should return `None`
- existing `add` and normal `divide` behavior should keep working
