
[BACK HOME](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/home.md)


# ACT Examples

## Common setup

This set of examples show the capabilities of the ACT software in a scenario
of Bioinformatics analysis. It is expected to have already available a valid
Microsoft Azure subscription, as well as, created a Storage Account and
Batch Account.

## 1. PRODIGAL - Parallelizing Gene Prediction Tasks From Large-Scale Metagenomic Data

The prodigal
This example includes the analysis of more than 5000 **.fasta** files, that contain
genomic data and have extremely heterogeneous sizes, ranging from 500kb to 35Gb.

In cases like this, the different inputs have to be carefully accounted
for, since the big inputs require massive amount of CPU and memory to be executed
plus a good disk space management to avoid system crashes such as memory limit,
disk full and other major perfomance and resource problems.

**The solution of these issues could lead** to **high costs and performance loss**,
if we use a high performance machine for all inputs, **or to complicated designs**,
like partitioning the input sets in series of inputs by size and assign different
VM for each set. Also, these perfomance problems could lead to many hours of debug
and testing to be uncovered, posing many challenges to the development of those analysis.

This is the perfect scenario to use ACT to create Tasks with a calculated custom
task slot for each one. To do this we used the **taskSlotFormula** from the
**tasks -> inputs** configuration.
```json
"taskSlotFormula": [
  "vmMemorySize = 32000000000",
  "maxTaskSlotSize = vmMemorySize / $pool.taskSlotsPerNode",
  "calculatedSlots = int(input_size/maxTaskSlotSize) + 1",
  "requiredSlots = calculatedSlots if (input_size > maxTaskSlotSize) else 1"
]
```

This attribute is a vector of strings, each one representing a statement written
using Python language. The statements represent each line in the code to calculate
the **requiredTaskSlots** of each  Task.

```python
vmMemorySize = 32000000000
```
It is possible to reference another configuration attribute using the symbol **$**
(dollar sign) and **.** (dot) to follow the json hierarch to the attribute you need:

```python
maxTaskSlotSize = vmMemorySize / $pool.taskSlotsPerNode
```
In those statements most of Python builtin functions are restricted,
the only functions allowed to use are:
**'abs', 'all', 'any', 'bin', 'bool', 'chr', 'float', 'str', 'hash', 'int', 'len', 'max',
'min', 'ord', 'range', 'sum', 'reversed', 'round', 'sorted', 'filter', 'format'**

```python
calculatedSlots = int(input_size/maxTaskSlotSize) + 1
```


```python
requiredSlots = calculatedSlots if (input_size > maxTaskSlotSize) else 1
```


[BACK HOME](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/home.md)