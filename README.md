# add text to gif cli app

simple CLI application with `python3` and `pillow` library for adding text on gif.

### usage

```
pip3 install -r requirements.txt
python3 ./main.py -h #for help
python3 ./main.py -i inp.gif -o out.gif -t "my text" -f ./fonts/Caprice.ttf
```

-   read with `-i` from `inp.gif`
-   add text `my text` to gif
-   use ttf font with `-f`, there are some beautiful fonts in `./fonts` dir.
-   write output with `-o` to `out.gif`

## example
```bash
./main.py -t "good night my dear" -i gn.gif -o out.gif  -p "0.1,0,0.9,0.15" -c "240,10,150"  -f ./fonts/Cup\ and\ Talon.ttf

```
