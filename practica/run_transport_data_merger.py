from practica.practica_1.scripts import spider_runner, data_merger

print("Running scrap...")
scrap_filename = spider_runner.main()
print("Scrap process finished.")
print("Merging scrap results with stops file.")
data_merger.main(scrap_filename)
print("Merge process finished.")

