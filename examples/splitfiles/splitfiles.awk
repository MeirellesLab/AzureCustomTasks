#!usr/bin/awk -f

BEGIN {
  fileno=1cd
}
{
  size += length()
}
size > 500000000 && />/ {
  fileno++
  size = 0
}
{
  split(FILENAME,file,".")
  filenum = sprintf("_part%02d.", fileno)
  print $0 > "../splits/" file[1] filenum file[2];
}
