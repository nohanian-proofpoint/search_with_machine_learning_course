for epoch in 5 25 40 ; do 
    for mincount in 5 25 40 ; do
      ~/fastText-0.9.2/fasttext skipgram -epoch $epoch -minCount $mincount -input /workspace/datasets/fasttext/normalized_titles.txt -output "/workspace/datasets/fasttext/exp_title_model_${epoch}_${mincount}"
    done
done
