
[BACK HOME](home.md)


# ACT Examples


This set of examples show the capabilities of the ACT software in a scenario of Bioinformatics analysis.

Before you start, you need to create or already have an account in the [Microsoft Azure Portal](https://portal.azure.com/). Then, log into the Portal and do the following steps:

* Create a Storage Account, your containers (input/output/scripts can be in the same container) and a SAS Token to access them.
* Create a Batch Account and link it to your Storage Account.
* Fill the configuration file with your data, specifically **all batch and storage parameters**.
* Upload the example script and input blobs to the defined container and path, accordingly with what is in the configuration file.

## 1. PRODIGAL - Parallelizing Gene Prediction Tasks From Large-Scale Metagenomic Data

The [Prodigal Software](https://github.com/hyattpd/Prodigal) is a [widely used](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-11-119) tool, developed to  predict protein-coding genes in prokaryotic genome data. Prodigal is known to be fast and accurately handle draft genomes, metagenomes, reconizing gaps, partial genes and identifying translation initiation sites.

The analysis of metagenomic data poses big challenges since it may contain files of many gigabytes. This has to be carefully accounted for, since it requires a massive amount of CPU and memory to be executed, plus a good data space management to avoid system crashes such as memory limit, disk full and other major perfomance and resource problems.

In our scenario we had to analyze more than 7000 **.fasta** files (containing the sequencing data) of heterogeneous sizes, ranging from 500kb to 35Gb, with a total of more than 8TB.

**The solution to those issues could lead** to **high costs and performance loss**, if we had used a high performance machine for all inputs, **or to complicated designs**, like partitioning the input sets in series of inputs by size and assign different VM for each set. Also, these perfomance problems could lead to many hours of debug and testing to be uncovered, challenging the development of those analysis.

In this example we have 10 files to show the capability of ACT to create Tasks with a calculated custom required slot for each one. To do this we used the **requiredSlotFormula** field, from the **tasks.inputs** configuration. Our slot formula was definied as follows:

```json
"requiredSlotFormula": [
  "vmMemorySize = 32000000000",
  "maxTaskSlotSize = vmMemorySize / $pool.taskSlotsPerNode",
  "calculatedSlots = int(input_size/maxTaskSlotSize) + 1",
  "requiredSlots = calculatedSlots if (input_size > maxTaskSlotSize) else 1"
]
```

This attribute is a vector of strings, each one representing a statement written using Python language. The statements represent each line of code to calculate the **requiredSlots** of each Task that has to be used in conjunction with the **taskSlotsPerNode** from the pool configuration.

```python
vmMemorySize = 32000000000
```
It is possible to reference another configuration attribute using the symbol **$** (dollar sign) and **.** (dot) to follow the json hierarch to the attribute you need:

```python
maxTaskSlotSize = vmMemorySize / $pool.taskSlotsPerNode
```
In those statements most of Python builtin functions are restricted, the only functions allowed to use are: **'abs', 'all', 'any', 'bin', 'bool', 'chr', 'float', 'str', 'hash', 'int', 'len', 'max', 'min', 'ord', 'range', 'sum', 'reversed', 'round', 'sorted', 'filter', 'format'**

```python
calculatedSlots = int(input_size/maxTaskSlotSize) + 1
```


```python
requiredSlots = calculatedSlots if (input_size > maxTaskSlotSize) else 1
```


[BACK HOME](home.md)
