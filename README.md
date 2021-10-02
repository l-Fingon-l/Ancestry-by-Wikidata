<h1 align="center">Ancestry by Wikidata</h1>

<h2 align="center">Try it out!</h2>

<div align="center">

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1B4B5yrb6KoRsJcxEQasX3AnSWWXmohHc?usp=sharing#scrollTo=aTFF2WVgn59W) or
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/l-Fingon-l/Ancestry-by-Wikidata/visual_improvements?labpath=source%2FRoyal%20Ancestry.ipynb)

Ever wondered if a particular person was a descendant of another? Was curious to find out whether current Prince William is an heir of King James II of England?  
Or, perhaps, just wanted to exami someone's genealogical tree?  
These kinds of questions are incredibly easy to explore with the help of this toolset. Moreover, it can be quite fun and exciting as well!  
</div>

---
<h2 align="center">How to use:</h2>
<div style="align-items:center;display:flex;flex-wrap:wrap;justify-content:space-around;">

1.Go to one of the interactive notebooks listed above and run the code:  
![code-cell-highlighted](illustrations/code-cell-highlighted.png)

2.Get the live interactive output. As simple as that!  
![output](illustrations/output.png) 
</div>

## So What Do I Need To Know?
This is a simple script for getting out the royal ancestry data from Wikidata.  
There are 3 different ways to get the job done. You may toggle them with the <ins>"**optimized**"</ins> button.


*   The ***first*** one is quite beautiful and insightful.
*   The ***optimized*** one is A LOT faster (~50x) but is not so spectacular to watch after. You may want to use it for long queries or just to get a simple answer **yes** / **no** to your query.
*   In case you just want to see the <ins>**family tree**</ins>, use the ***unlimited_depth*** option (this one is designed for the unoptimized version). It turns the depth restrictions off. The search will be much slower, though.

Run the search by providing 2 sources: the ***descendant*** and the ***ancestor***.
You may provide them in many ways:


*   By article name: **Emma Watson**
*   By url from English Wikipedia: **en.wikipedia.org/wiki/Emma_Watson**
*   By Wikidata item ID: **Q39476**

You may even open the [main.py](source/main.py) code snippet and choose one of the pre-described people.

<ins>**Don't be afraid** to change the parameters!</ins> This is what actually makes this notebook so interactive and fun!  
![parameters](illustrations/parameters.png)

---
<h2 align="center">It all began on a rainy...</h2>
It all began with me learning Irish. Well, it all began with me learning Scottish Gaelic. In fact, I've been fascinated by Сeltic culture, literature, music and language for as long as I can remember. I have had no serious intentions of giving a try to such an exotic language ever since I hadn't succeeded in my Sindarin attempts a couple of years ago, though.  
And then.. the covid struck.  

I have suddenly got plenty of time on my hands. And I decided to give it a go. However, quite soon I realised, the amount of different learning materials, such as videos, songs and simply dictionaries was way richer for it's twin-language - Irish Gaeilge. Not long after I'd come across an "Irish language and culture" course by Dublic City University and enrolled immediately.  

The course was great, for sure. But it lacked the practice which I have always considered the backbone for any learning process. Thus, I tried to enrich the acquisition by Irish folk songs which came incredibly handy. There was one I loved exceptionally, called Siúil a Rún.  

Our journey starts on a grey, rainy morning as I was listening to the song for the 40th time in a row while scrolling down the comments section. And I have suddenly stumbled upon [this very comment](https://www.youtube.com/watch?v=UYHoZQD2rsc&lc=UgwNlj3GE9OIofsk6PF4AaABAg.9MJPjNkGXfl9NXzI_PNHed). The latter part of its.  
Damn! That made me curious as never before. As a huge fan of the Royal Family, I became ought to find out if the statement was true. So I started googling the subject, but... I could find no trace. I've surfed though dozens of dedicated sites but could not find a single clue.  
Well, in the end there'd been a source of knowledge that *should* have had the answers. The <ins>**Wikipedia**</ins>.  

---
## Python & Wikidata API
It didn't take long till I realised the absurdity of the very idea of me manually traversing the genealogical tree from 2000s all the way back to 1600s. That meant, I had to ask my computer for aid! And so I did.  

I had *very* little knowledge of Python at that moment. Besides, I'd played with it just once before (I wouldn't even dare calling it **usage**, - all I did was to copy and run some sample code from StackOverflow which was meant to send a bunch of e-mails). I did know, nevertheless, it was exceptionally tuned for data manipulations. 

Half an hour later the first iteration of the algorithm was ready. It consisted of a very straightforward depth-first-search implementation which was displayed beautifully in real time as the algorithm was quering the Wikidata. And honestly, it was enough to solve my problem: I ran the test and got the answer in about 2 hours.  
```  
    James II of England  
              ||          
              \/         
    Henrietta FitzJames
              ||          
              \/         
    James Waldegrave, 1st Earl Waldegrave
              ||          
              \/         
    James Waldegrave, 2nd Earl Waldegrave
              ||          
              \/         
    Anne Horatia Waldegrave
              ||          
              \/         
    Horace Seymour
              ||          
              \/         
    Adelaide Seymour
              ||          
              \/         
    Charles Spencer, 6th Earl Spencer
              ||          
              \/         
    Albert Spencer, 7th Earl Spencer
              ||          
              \/         
    John Spencer, 8th Earl Spencer
              ||          
              \/         
    Diana, Princess of Wales
              ||          
              \/         
    Prince William, Duke of Cambridge
```
The comment was indeed right! Prince William was, in fact, a descendant of King James II of England! To put it in a nutshell, that was all I wished: I used the tools available to get the result I was interested in. Still, hence the tools are possible to forge, is there a way to sharpen them? 

---
## Improvements
The depth of the search seemed to be the main issue. Its limitations would inevitably lead to query speed boost.  

### Some sophisticated algorithmical tricks were included in the first series of enhancements included, such as:
* improved **dates** of life usage
* **spouse**'s lifespawn usage
* WikiData item description analysis with **regexp** for missing lifespawn dates  

The benchmarks for the improvement algorithm as well as for the original one were added as well.  

### Architectural and interface refactorings
Despite the fact these changes were not huge and had no visible impact on the algorithm, they were added as a vital step preceding the future extensions, contrary to those of the previous iteration.

### Powerful parallelistic optimizations
It was quite obvious at that point (well, long before that. I just used to ignore that fact as it would've ruined the algorithmic approach) that the **bottleneck** of the system as a whole was in **queries** to WikiData themselves. These optimizations took advantage of both the WikiMedia API allowing to ask for up to 50 data items at once and the asynchronous item handling functions. In spite of all the anticipation I got, the latter did not seem to speed up the runs by more than 2-3%. The former's impact was unprecedented, on the other hand: the optimized version's benchmarks indicated as much as up to 50X perfomance gains.  

### UTF-8 & other language wikis' support
The final strokes. Had nothing to do with the perfomance, nonetheless added additional layer of comfort to the interface.

---
## Jupyter notebooks
Brilliant! The project is ready, it is fast and it allows me to do some fun stuff I would never be able to do on my own. There was only pazzle left: ***How do I share my work?*** I had this awesome Python script, but what it is all about if I can't even show it to the others?  
It could've been the case, my grannie would've been able to download the script from the web. She could have been even possibly able install the Python interpreter. But that would mean the hassle. That would take her time and would almost certainly diminish the joy she would otherwise get from this toy. Something should've been done about this.  

Packing ***.py*** into ***.exe***? Possible but the hassle is still there.  
Creating a dedicated website to run Python script in the back-end? Possible. As a drawback, the code would be way too difficult to see then.  
However, a superior solution existed: Jupyter notebook. This kind of document allows you to mix text and Python code altogether. Moreover, you could basically run it from the very notebook. Excellent!

In this project I use 2 different Jupyter Notebook hosting services: Google Colab & MyBinder. They share a fair amount of similarities, although there are some differences to be noted. Mainly:
* Google Colab provides us with an extremely convenient way to parametrize the code. Binder does not have this feature and you'll have to change the code manually (even though it's fairly simple and straightforward of a task)
* MyBinder does not require an account. You might need an existing Google account to use the Colab
* It is not so easy to use additional (.py) files in Google Colab's notebook. This leads to the whole codebase being added to the notebook itself. There is an option to hide the cell's core code, nonetheless, which comes pretty handy.  
What this means is the pictures will not be a part of a notebook, as well. Which is not the case for MyBinder.

<h2 align="center">So, what are you waiting for? Try it out yourself!</h2>

<div align="center">

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1B4B5yrb6KoRsJcxEQasX3AnSWWXmohHc?usp=sharing#scrollTo=aTFF2WVgn59W) or
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/l-Fingon-l/Ancestry-by-Wikidata/visual_improvements?labpath=source%2FRoyal%20Ancestry.ipynb)