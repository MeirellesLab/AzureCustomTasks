
[BACK HOME](home.md)


# ACT Examples


This set of examples show the capabilities of the ACT software in a scenario of Bioinformatics analysis.

Before you start, you need to create or already have an account in the [Microsoft Azure Portal](https://portal.azure.com/). Then, log into the Portal and do the following steps:

* Create a Storage Account, your containers (input/output/scripts can be in the same container) and a SAS Token to access them.
* Create a Batch Account and link it to your Storage Account.
* Fill the configuration file with your data, specifically **all batch and storage parameters**.
* Upload the example script and input blobs to the defined container and path, accordingly with what is in the configuration file.

## 1. PRODIGAL - Parallelizing Gene Prediction Tasks From Large-Scale Metagenomic Data

The [Prodigal Software](https://github.com/hyattpd/Prodigal) is a [widely used](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-11-119) tool, developed to predict protein-coding genes in prokaryotic genome data. Prodigal is known to be fast and accurately handle draft genomes and metagenomes, reconizing gaps, partial genes and identifying translation initiation sites.

In our scenario we had to analyze metagenomics sequencing data of more than 7000 *.fasta* files, with heterogeneous sizes ranging from 500kb to 35Gb, that sum up more than 8TB of data.

The analysis of metagenomic data poses big challenges, specialy when we use large datasets. This has to be carefully accounted for, since it requires a massive amount of CPU and memory to be executed, plus a good data space management to avoid system crashes such as memory limit, disk full and other major perfomance and resource problems.

**The solution to those issues could lead** to **high costs and performance loss**, if we use a high performance machine for all inputs, **or to complicated designs**, like partitioning the input sets in series of inputs by size and assign different VM for each set. Also, these perfomance problems could lead to many hours of debug and testing to be uncovered, challenging the development of those analysis.

In this example we have 10 files to show the capability of ACT to create Tasks with a custom required slot for each one. To do this we used the **requiredSlotFormula** field, from the **tasks.inputs** configuration. 

```json 
"requiredSlotFormula": [
  "vmMemorySize = 32000000000",
  "maxTaskSlotSize = vmMemorySize / $pool.taskSlotsPerNode",
  "calculatedSlots = int(input_size/maxTaskSlotSize) + 1",
  "requiredSlots = calculatedSlots if (input_size > maxTaskSlotSize) else 1"
]
```
This attribute is a vector of strings, each one representing a statement written using Python language. The statements represent each line of code to calculate the **required_slots** attribute of each Task. This must be used in conjunction with the **task_slots_per_node** from the pool configuration, to determine how many slots each computing node will have to assign to Tasks, which must also take into account how many cpu cores your compute nodes have, accordingly with the configured **vm_size**. 

* These statements can be as simple as an assignment:

```python
vmMemorySize = 32000000000
```

* Can refer to another configuration attribute using the characters '**$**' (dollar sign) and '**.**' (dot) to follow the json hierarch to it, like in:

```python
maxTaskSlotSize = vmMemorySize / $pool.taskSlotsPerNode
```

* Most of Python functions are restricted, but you are allowed to use the following functions: **abs, all, any, bin, bool, chr, float, str, hash, int, len, max, min, ord, range, sum, reversed, round, sorted, filter, format**. 

* We also have access to the input_name and input_size from each input, so this calculation can use these variables to make this result specific to the input characteristics.

```python
calculatedSlots = int(input_size/maxTaskSlotSize) + 1
```

* In the end of these formulas you must assign the appropriate value to the variable **requiredSlots**, if you don't do it the **default** value for this variable is 1. The **requiredSlots** will be used to designate how many computing nodes will be used for each Task.

```python
requiredSlots = calculatedSlots if (input_size > maxTaskSlotSize) else 1
```

This configuration will allow our Tasks to use the necessary resources for our input size, the following table shows how we used our resources in our case:

| --- | --- | --- | --- | --- |
| INPUT | SIZE | REQUIRED_SLOTS | COMPUTE TIME | COST |
| --- | --- | --- | --- | --- |
| mgm1238321 | 1.5MB | 1 | 25s | $ 0.001 |
| mgm1239072 | 15MB | 1 | 87s | $ 0.004 |
| mgm1238321 | 150MB | 1 | 25s | $ 0.001 |
| mgm1239072 | 500MB | 1 | 87s | $ 0.004 |
| mgm1238321 | 1000MB | 2 | 25s | $ 0.001 |
| mgm1239072 | 5000MB | 10 | 87s | $ 0.004 |
| mgm1238321 | 10000MB | 20 | 25s | $ 0.001 |
| mgm1239072 | 15000MB | 30 | 87s | $ 0.004 |


[BACK HOME](home.md)
