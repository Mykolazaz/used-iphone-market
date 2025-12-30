# Used iPhone Market Analysis

This is a Python data scraping and analysis project with Selenium & Pandas.

The main aim of this project is to analyse used iPhone listings in Lithuania based on features such as model, price, city, condition, description, etc and suggest improvements that could be implemented by the platform.

The data was scraped from [Skelbiu.lt](https://skelbiu.lt/), the most popular Lithuanian advertisement platform.

When analysings the dataset, many insights became apparent:

- 81% of listings were concentrated in TOP 5 cities and only 5% of iPhones were available in 2 or more locations. To remedy the situation, text suggesting sellers mark multiple locations should be added in the listing creation page. The additional text effectiveness should be tested with described A/B test;

- TOP 5% of listings accounted for 50% of views, meaning that the discovery rate for some listings must be low. A discussion with the Data Science team is necessary to make sure recommendation models are not too biased towards ads with large amount of views and new posts are being shown;

- Listings for iPhone accesories were found to be miscategorized in iPhone category in order to attract more views. Listing quality standarts should be discussed to check if this is a one-time occurance or a platform-wide problem;

- 380 iPhones were found to be overpriced (25% above median). A 'recommended price' feature could be implemented in the listing creation screen for sellers. It would encourage sellers to list iPhones for lower prices. On the buyers' side, an underpriced iPhone would receive a 'great price' icon;

- Tests showed that there were statistically significant differences between iPhone 13 prices in the TOP 3 cities for the same model. Previously mentioned 'recommended price' feature could help equalize prices;

- 231 iPhone listings were missing either a price, a description or a phone condition. A trivial solution is possible: adding suggestive text above the description input field stating that '98% of sold items had a description'. A more complex solution could be implementing a scoring system that assigns points for every filled out field and uploaded photo.


AI was used for statistical test code debugging and KPI suggestions.