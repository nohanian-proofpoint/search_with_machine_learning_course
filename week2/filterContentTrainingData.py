import argparse
import pprint

parser = argparse.ArgumentParser(description='')
general = parser.add_argument_group("general")
general.add_argument("--input")
general.add_argument("--output")
general.add_argument("--min_products", default=0, type=int, help="The minimum number of products per category (default is 0).")


def main(input_file, output_file, min_products):
    print("Input file: %s" % input_file)
    print("Writing results to %s" % output_file)
    print("min_products=%s" % min_products)
    category_productName_list = []
    category_count = {}
    line_count = 0
    for line in open(input_file, 'r').readlines():
        line_count+=1
        #print("line: {}".format(repr(line)))
        category, productName = line.strip().split(" ",1)
        category_productName_list.append((category, productName))
        category_count[category] = category_count.get(category, 0) + 1

    print("total categories: {}".format(len(category_count)))
    #pprint.pprint(category_count)

    final_categories = []
    for category in category_count:
        if category_count[category] >= min_products:
            final_categories.append(category)

    print("pruned categories: {}".format(len(final_categories)))

    with open(output_file, 'w') as out:
        for category, productName in category_productName_list:
            if category in final_categories:
                out.write("{} {}\n".format(category, productName))
    print("done.")


if __name__ == '__main__':
    args = parser.parse_args()
    output_file = args.output
    main(args.input, args.output, int(args.min_products))
