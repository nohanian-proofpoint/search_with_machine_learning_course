import argparse
import pprint
import fasttext


parser = argparse.ArgumentParser(description='')
general = parser.add_argument_group("general")
general.add_argument("--topwords")
general.add_argument("--model")
general.add_argument("--threshold")
general.add_argument("--output", default="synonyms.csv")


def main(topwords_file, model_file, threshold, output_file):
    print("topwords file: %s" % topwords_file)
    print("model file: %s" % model_file)
    print("Writing results to %s" % output_file)
    model = fasttext.load_model(model_file)
    with open(output_file, 'w') as out:
        for line in open(topwords_file, 'r').readlines():
            word = line.strip();
            print("word: {}".format(word))
            line_items = [word]
            neighbors = model.get_nearest_neighbors(word)
            for similarity, synonym in neighbors:
                if similarity>=threshold:
                    line_items.append(synonym)
            out.write(",".join(line_items) + "\n")
    print("done.")


if __name__ == '__main__':
    args = parser.parse_args()
    main(args.topwords, args.model, float(args.threshold), args.output)
