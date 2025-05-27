# merge_urls.py

def merge_files(before_file, after_file, output_file):
    with open(before_file, 'r', encoding='utf-8') as f_before, \
         open(after_file, 'r', encoding='utf-8') as f_after, \
         open(output_file, 'w', encoding='utf-8') as f_out:

        for before_line, after_line in zip(f_before, f_after):
            before_line = before_line.strip()
            after_line = after_line.strip()
            f_out.write(f"{before_line}\t{after_line}\n")

# ファイル名の指定
merge_files('goo.txt', 'fc2.txt', 'merged.txt')

