# How to select compute nodes
Selecting compute nodes is very important for your Spark cluster.

If you will be performing large shuffles then you should prefer nodes with fast local
storage. A minimum requirement is approximately 500 MB/s. Drives that can deliver 2 GB/s
are ideal.

- Any modern SSD should be sufficient.
- A spinning disk will be too slow.
- An HPC shared filesystem (e.g., Lustre) will be slower than an SSD, but is likely sufficient.
- A RAM drive (e.g., `/dev/shm`) will work well for smaller data sizes. Many HPC compute nodes have these.
- If the size of the data to be shuffled is greater than the size of the nodes' SSDs, then
you'll need to either add more nodes or use the shared filesystem.
