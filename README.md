# sanitizing

Using only darpan21 (120k) and FCRA  (20k) data sets. The rest is unwieldy stuff and unnecessary for right now.
In both files, NGO names and registration state names had to be cleaned.
Various nulls are dropped
Much of the duplpication of NGO names is disambiguated or deduped by also using reg state. So for example there are 31 "CATHOLIC CHARITIES" but when you cross with regisration state most become unique.
I match the two tables on both clean name and clean state. This is darpan21 left join FCRA, so all valid darpan NGOs are preserved (112k). I think I understand why this is a smaller table than 119k.
I give primacty to the FCRA number from the FCRA data, else use the darpan data if available. 11k + 23k -> 24k of the above 112k that also have FCRA numbers.
I split "issues" and created a reverse look up dictionary (rather than one hot encoding). There is a one-time cost of creating the dict but then performance is faster. Each of the 44 issues has a list of darpan UniqueIDs.
I spplit the "operating states" (after cleaning the names) and created a reverse look up dict. There are 36 states/UTs, each with a list of darpan uniqueIDs.
Then, just as a proof of concept, I selected 3 issues (union: 221+ 15k + 8k = 17k) and 2 states (union: 170+244 = 346) and looked at the interesction of the above two (116) with the set of IDs that have an FCRA number (24k) to yield a final list of 30 NGOs.
Additional data can be used, e.g.  does it have a webpage, is there an e-mail contact etc ... to reduce the list further.
So in my opinion, this is ready to go live. I can upload the code and the data files to github, where @Rohan Varma can pick it up. If people think otherwise, let me know what else needs to be done or what other directions we are pursuing.
