import os,sys
import datetime

def print_output(metagenomes, filename):
    res_profile = ["RF0001","RF0002","RF0003","RF0004","RF0005","RF0006",
                   "RF0007","RF0019","RF0020","RF0021","RF0022","RF0023",
                   "RF0026","RF0027","RF0028","RF0029","RF0030","RF0033",
                   "RF0034","RF0035","RF0036","RF0037","RF0040","RF0041",
                   "RF0042","RF0043","RF0044","RF0046","RF0047","RF0048",
                   "RF0049","RF0050","RF0051","RF0052","RF0053","RF0054",
                   "RF0055","RF0056","RF0057","RF0059","RF0062","RF0064",
                   "RF0065","RF0066","RF0067","RF0068","RF0069","RF0070",
                   "RF0071","RF0072","RF0074","RF0076","RF0078","RF0080",
                   "RF0081","RF0082","RF0083","RF0084","RF0087","RF0088",
                   "RF0089","RF0090","RF0091","RF0094","RF0096","RF0097",
                   "RF0098","RF0099","RF0100","RF0101","RF0104","RF0105",
                   "RF0106","RF0107","RF0108","RF0109","RF0111","RF0112",
                   "RF0113","RF0114","RF0115","RF0116","RF0117","RF0118",
                   "RF0119","RF0120","RF0121","RF0122","RF0123","RF0124",
                   "RF0125","RF0126","RF0127","RF0128","RF0129","RF0130",
                   "RF0131","RF0132","RF0133","RF0134","RF0135","RF0136",
                   "RF0137","RF0147","RF0149","RF0150","RF0151","RF0152",
                   "RF0153","RF0154","RF0155","RF0156","RF0157","RF0158",
                   "RF0159","RF0160","RF0161","RF0162","RF0166","RF0174",
                   "RF0172","RF0173","RF0168"]

    with open(filename, 'w') as file:
        file.write(f"metagenome_id,{','.join(res_profile)},total\n")
        for (meta_id,res) in metagenomes.items():
            res_str = ','.join([str(res.get(x,0)) for x in res_profile])
            res_sum = sum([res[x] for x in res])
            file.write(f'{meta_id},{res_str},{res_sum}\n')


def parse_hmmer_file(inputpath):
    filelist = []
    for (dirpath, dirnames, filenames) in os.walk(inputpath):
        for file in filenames:
            if file.endswith("_modelo.txt"):
                filelist.append(f'{dirpath}/{file}')
    print(f'Found {len(filelist)} files.')

    metagenomes = {}
    for filename in filelist:
        print(f'Processing file: {filename}')
        metagenome_id = filename.split('/')[-1].split('_')[0]
        if metagenome_id not in metagenomes:
            metagenomes[metagenome_id] = {}
        resistome = metagenomes[metagenome_id]

        with open(filename, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                if line.startswith('#'):
                    continue
                tokens = line.split(maxsplit=18)
                accession = tokens[1]
                if accession in resistome:
                    resistome[accession] += 1
                else:
                    resistome[accession] = 1
    return metagenomes


if __name__ == '__main__':
    """
    Redirects the main execution to the main function.
    """
    start_time = datetime.datetime.now().replace(microsecond=0)
    rootpath = os.getenv('AZ_BATCH_NODE_MOUNTS_DIR')
    metagenomes = parse_hmmer_file(f'{rootpath}/{sys.argv[1]}{sys.argv[3]}')
    outputpath = f'{rootpath}/{sys.argv[2]}'
    try:
        os.mkdir(outputpath)
    except:
        pass
    print_output(metagenomes,f"{outputpath}{sys.argv[3].replace('/','_')}.csv")
    # Print out some timing info
    end_time = datetime.datetime.now().replace(microsecond=0)
    print(f'Script end: {end_time}')
    print(f'Elapsed time: {end_time-start_time}')
    print('Execution finished!')
