2017-11-23T09:10+08:00

```csharp
var objs = new object[] { 42, 3.14, 8080, "Hello, world!", 21 };

// Print all integers in objs
foreach (var i in objs.Where(elem => elem is int).Cast<int>())
    Console.WriteLine(i);
    
// Use `OfType` instead of `Where`+`Cast`
foreach (var i in objs.OfType<int>())
    Console.WriteLine(i);
```

C# 6.0 in a Nutshell

>Cast and OfType differ in their behavior when encountering an input element that’s of an incompatible type. Cast throws an exception; OfType ignores the incompatible element.
>
>The internal implementation of OfType:
>
```csharp
public static IEnumerable<TSource> OfType <TSource> (IEnumerable source)
{
    foreach (object element in source)
        if (element is TSource)
            yield return (TSource)element;
}
```

>Cast has an identical implementation, except that it omits the type compatibility test:
>
```csharp
public static IEnumerable<TSource> Cast <TSource> (IEnumerable source)
{
    foreach (object element in source)
        yield return (TSource)element;
}
```

2017-11-23T09:27+08:00

[corefx:Take.cs](https://github.com/dotnet/corefx/blob/master/src/System.Linq/src/System/Linq/Take.cs)

```csharp
namespace System.Linq
{
    public static partial class Enumerable
    {
        public static IEnumerable<TSource> Take<TSource>(this IEnumerable<TSource> source, int count)
        {
            if (source == null)
            {
                throw Error.ArgumentNull(nameof(source));
            }

            if (count <= 0)
            {
                return EmptyPartition<TSource>.Instance;
            }

            if (source is IPartition<TSource> partition)
            {
                return partition.Take(count);
            }

            if (source is IList<TSource> sourceList)
            {
                return new ListPartition<TSource>(sourceList, 0, count - 1);
            }

            return new EnumerablePartition<TSource>(source, 0, count - 1);
        }
    }

    ......
}
```

This is an example of [Pattern matching with is](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/is) starting with C# 7.

```csharp
object a = 1;
Console.WriteLine(a is int); // True

// Type matching with `is` starting with C# 7.
// expr is type varname
if (a is int b)
{
    // CS0019 Operator '+' cannot be applied to operand of type 'object' and 'int'
    //Console.WriteLine(a + 1);
    
    // OK
    Console.WriteLine(b + 1); // 2
}
```

We can simplify the implementation of `OfType` now:

```csharp
public static IEnumerable<TSource> OfType <TSource> (IEnumerable source)
{
    foreach (object element in source)
        if (element is TSource target)
            yield return target;
}
```

By the way, the implementation of `IPartition`, `ListPartition` can be found in [corefx::Partition.cs](https://github.com/dotnet/corefx/blob/master/src/System.Linq/src/System/Linq/Partition.cs).

`TakeWhile` and `Where`:

```csharp
var names = new string[]
{
    "Tom",
    null,
    "Jerry",
    "Lucy",
    "",
    "John",
};

foreach (var name in names.TakeWhile(name => !string.IsNullOrWhiteSpace(name)))
    Console.WriteLine(name);

foreach (var name in names.Where(name => !string.IsNullOrWhiteSpace(name)))
    Console.WriteLine(name);

// References:
// https://stackoverflow.com/questions/12397880/using-linq-how-to-select-conditionally-some-items-but-when-no-conditions-select
```

```csharp
public static class MyFunkyExtensions
{
    public static IEnumerable<TResult> ZipThree<T1, T2, T3, TResult>(
        this IEnumerable<T1> source,
        IEnumerable<T2> second,
        IEnumerable<T3> third,
        Func<T1, T2, T3, TResult> func)
    {
        using (var e1 = source.GetEnumerator())
        using (var e2 = second.GetEnumerator())
        using (var e3 = third.GetEnumerator())
        {
            while (e1.MoveNext() && e2.MoveNext() && e3.MoveNext())
                yield return func(e1.Current, e2.Current, e3.Current);
        }
    }
}

// References:
// [How to combine more than two generic lists in C# Zip?](https://stackoverflow.com/questions/10297124/how-to-combine-more-than-two-generic-lists-in-c-sharp-zip)
```

[Generate number sequences with LINQ](https://stackoverflow.com/questions/2737090/generate-number-sequences-with-linq)
> Enumerable.Range(start, count);

[How do you do *integer* exponentiation in C#?](https://stackoverflow.com/questions/383587/how-do-you-do-integer-exponentiation-in-c)
```csharp
public static int Pow(this int bas, int exp)
{
    return Enumerable
          .Repeat(bas, exp)
          .Aggregate(1, (a, b) => a * b);
}
```

