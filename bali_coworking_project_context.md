# Bali Coworking Spaces Dataset -- Project Context

This document summarizes the research and data collected so far for a
dataset of coworking spaces in Bali suitable for remote work.\
The goal is to continue the work with an automated coding agent
(e.g. Gemini CLI) that can enrich and verify the dataset.

The emphasis is on **spaces that allow late‑night or overnight work**.

------------------------------------------------------------------------

# Geographic Scope

Coworking spaces located roughly within **1--1.5 hours travel from
Denpasar**.

Relevant areas include:

-   Canggu
-   Pererenan
-   Sanur
-   Seminyak
-   Kerobokan
-   Kuta
-   Ungasan / Uluwatu (Bukit peninsula)
-   Ubud

------------------------------------------------------------------------

# Classification of Coworking Spaces

Spaces are categorized based on **member access hours**.

## 1. Overnight coworking

Members can access the space **24/7**.

## 2. Late‑night coworking

Members can work **until \~22:00--00:00**.

## 3. Daytime coworking

Spaces that close earlier in the evening.

These are included for completeness but are **less suitable for
late‑night remote work**.

------------------------------------------------------------------------

# Dataset Collected So Far

## Overnight Coworking (24/7 member access)

  name              area                website                         access_time
  ----------------- ------------------- ------------------------------- ---------------
  BWork             Canggu              https://bwork.id                24/7
  Tropical Nomad    Canggu              https://tropicalnomad.id        24/7
  BukitHub          Ungasan / Uluwatu   https://bukithub.com            24/7
  Livit Hub         Sanur               https://livit.co                24/7
  Outpost Ubud      Ubud                https://destinationoutpost.co   24/7
  Outpost Canggu    Canggu              https://destinationoutpost.co   24/7
  Biliq Coworking   Seminyak            https://biliq.com               24/7

## Late‑Night Coworking (\~22:00--00:00)

  name              area        website                      access_time
  ----------------- ----------- ---------------------------- ----------------
  ZIN@Work          Canggu      https://zinwork.com          \~06:30--00:00
  G88 Coworking     Kerobokan   https://g88coworking.com     \~07:00--00:00
  Tribal Bali       Pererenan   https://tribalbali.com       \~08:00--22:00
  Karya Coworking   Canggu      https://karyacoworking.com   \~07:00--22:00

## Daytime Coworking

  -----------------------------------------------------------------------------------------
  name              area              website                             access_time
  ----------------- ----------------- ----------------------------------- -----------------
  Genesis Creative  Pererenan         https://genesiscreativecentre.com   \~09:00--19:00
  Centre                                                                  

  Kinship Studio    Canggu            https://kinshipstudio.com           \~08:00--20:00

  Hubud             Ubud              https://hubud.org                   \~08:00--20:00

  Kembali           Seminyak          https://kembali.co                  \~09:00--17:00
  Innovation Hub                                                          

  GoWork Park23     Kuta              https://go-work.com                 \~09:00--18:00
  -----------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Target Dataset Structure

The dataset should for now contain the following columns.

  column            description
  ----------------- -------------------------------------
  name              coworking space name
  area              neighborhood or region in Bali
  website           official website
  pricing_page      direct link to pricing page
  access_time       hours members can stay in the space
  weekend_access    whether or not the space can be acccessed at weekends
  google_rating     Google Maps star rating
  google_reviews    Number of Google Maps reviews
  google_maps_uri   Google Maps link

------------------------------------------------------------------------

# Data Requirements

The following rules should be followed when enriching the dataset.

## Access Times and Days

The reported access times and days should be for weekly and monthly members, not day-pass users.

If reception closes earlier but members can stay inside, the space
should count as late‑night (e.g. reception closing at 18:00, but users can still keep working in the space).

Data should come preferably from the official website. If not available, it should come from verified user reports, reviews, etc.

------------------------------------------------------------------------

## Pricing Page

If available, include a **direct link to the pricing or membership
page** of the coworking space.

------------------------------------------------------------------------

## Google Maps Data

The following fields must be populated **exclusively using the Google
Places API**:

-   google_rating
-   google_reviews
-   google_maps_uri

These values **must NOT be taken from web search results or third‑party
websites**.

Required API fields:

-   rating
-   userRatingCount
-   googleMapsUri
-   id (Place ID)

API endpoint:

https://places.googleapis.com/v1/

Typical workflow:

1.  Resolve the coworking space using

POST /v1/places:searchText

2.  Extract the returned place ID

3.  Query

GET /v1/places/{PLACE_ID}

Fields:

rating\
userRatingCount\
googleMapsUri

------------------------------------------------------------------------

# Data Gathring and Research Process

The data gathering and research process should follow a "divide and conquer" ant iterative pattern:

- Research each data field (or groups of related data fields) separately
  - For example, research the access times for each coworking space as a separate research task. 
- Add data only to the final data set when it has been thoroughly researched and verified
- Build the data set up iteratively, i.e. for each missing part, start a new research task
- Ask the user for verification after each research task (e.g. show gathered data and source)

------------------------------------------------------------------------

# Preliminary Tasks

To start off, the following tasks should be done:

- Create scaffold for final data set
  - Decide on data format (JSON, CSV, etc.?)
  - Add only coworking space names and website URLs (the other data first has to be verified before adding it)
- Verify the existing data according to the research process described above and then re-add it to the data set
