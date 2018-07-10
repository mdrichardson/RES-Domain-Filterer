# Reddit Enhancement Suite Domain Filterer

This is a basic script I use to add biased media domains to Reddit Enhancement Suite's (RES) domain filter. For example, I used this to hide the most biased and untrustworthy news sources identified by [Media Bias Fact Check](mediabiasfactcheck.com) (about 450 unique domains) so that I no longer see them when browsing Reddit.

## Features

* Provides domain filters for RES using MediaBiasFactCheck
  * Supports the following categories (use as many at a time as you'd like):
    * Left Bias
    * Center-Left Bias
    * Least Biased
    * Center-Right Bias
    * Right Bias
    * Pro-Science
    * Conspiract-Pseudoscience
    * Questionable Sources
    * Satire
* File load/save using tKinter
* Web scraping using Requests
* Auto-opens web browser for help saving/loading RES settings

## Limitations

Note: All limitations only exist because this script did what it needed to do for me already; It's a one-time use script and I no longer need or use it.

* It's a little slow
  * Can be made better using multithreading/async
* Some domains have errors
  * MediaBiasFactCheck doesn't list the URLs uniformly, which makes it a bit of a hassle to ensure they all scrape appropriately
    * As a quick "fix", a list of error domains is printed at the end of the script so that users can them manually
* Media Bias Fact Check - I don't know how accurate they are, but I chose them as the source due to a lack of efficient alternatives
