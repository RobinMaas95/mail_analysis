"""Short analysis of the domains, top-level-domains and the geographical origin of mail addresses."""

from pathlib import Path

import geopandas
import matplotlib.pyplot as plt
import pandas as pd
import pycountry
import seaborn as sns
from pandas.core.frame import DataFrame

import mail_data

EXPORT_FILETYPE = "png"  # png, pdf, svg ... output format for the plots
TARGET_FOLDER = Path("results")  # Path to the folder where the plots will be saved

COUNTRIES_LATITUDE_LONGITUDE = (
    "https://raw.githubusercontent.com/melanieshi0120/"
    "COVID-19_global_time_series_panel_data/master/data/countries_latitude_longitude.csv"
)

COUNTRY_SPECIFIC_DOMAINS_TO_COUNTRY = {
    "ar": "Argentina",
    "au": "Australia",
    "be": "Belgium",
    "br": "Brazil",
    "ca": "Canada",
    "ch": "Switzerland",
    "cl": "Chile",
    "com": "Unknown",
    "de": "Germany",
    "dev": "Unknown",
    "edu": "Unknown",
    "es": "Spain",
    "fr": "France",
    "hk": "Hong Kong",
    "id": "Indonesia",
    "ie": "Ireland",
    "in": "India",
    "io": "Unknown",
    "it": "Italy",
    "jp": "Japan",
    "lr": "Liberia",
    "me": "Unknown",
    "mx": "Mexico",
    "ne": "Niger",
    "net": "Unknown",
    "nl": "Netherlands",
    "np": "Nepal",
    "ru": "Russian Federation",
    "sa": "Saudi Arabia",
    "sh": "Saint Helena, Ascension and Tristan da Cunha",
    "sk": "Slovakia",
    "uk": "United Kingdom",
    "us": "United States",
    "wtf": "Canada",
    "zw": "Zimbabwe",
}  # Source: https://www.worldstandards.eu/other/tlds/, extend to your needs


WORLD_COLUMNS = [
    "pop_est",
    "continent",
    "name",
    "country_codes",
    "gdp_md_est",
    "geometry",
]


def get_element_parts(
    original_list: list, splitter_character: str, split_index: int
) -> list:
    """
    Split all elements of the passed list on the passed splitter_character.

    Return the element at the passed index.

    Parameters
    ----------
    original_list : list
        List of strings to be split.
    splitter_character : str
        Character to split the strings on.
    split_index : int
        Index of the element to be returned.

    Returns
    -------
    list
        List with the elements at the passed index.
    """
    new_list = []
    for element in original_list:
        temp_element = element.rsplit(splitter_character)[split_index]  # split element
        temp_element = temp_element.strip()  # clean data
        temp_element = temp_element.casefold()  # force lower case
        new_list.append(temp_element)

    return new_list


def get_base_df(email_addresses: list) -> pd.DataFrame:
    """
    Return a dataframe with the columns email_addresses, domains and top_level_domains.

    Parameters
    ----------
    email_addresses : list
        List with all email addresses

    Returns
    -------
    pd.DataFrame
    """
    email_addresses = get_element_parts(email_addresses, "<", 0)
    email_addresses = list(filter(None, email_addresses))  # Remove empty strings
    domains = get_element_parts(email_addresses, "@", 1)
    top_level_domains = get_element_parts(domains, ".", -1)
    df = pd.DataFrame(
        {
            "email_addresses": email_addresses,
            "domains": domains,
            "top_level_domains": top_level_domains,
        }
    )

    return df


def rename_column_entries(
    df: pd.DataFrame, target_domain: str, new_domain: str, new_tld: str
) -> pd.DataFrame:
    """
    Rename all values for the entries with the target domain to the new domain and the corresponding
    email and toplevel domain.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with the columns email_addresses, domains and top_level_domains.
    target_domain : str
        Domain to be replaced.
    new_domain : str
        New domain to replace the target domain.
    new_tld : str
        New top level domain to replace the target domain.

    Returns
    -------
    pd.DataFrame
        Dataframe with the new values.
    """
    try:
        splitted_mail = (
            df[df.domains == target_domain].email_addresses.item().split("@")
        )
    except ValueError:
        # Raised when the target domain is not found in the df, no need for further processing
        return df
    corrected_mail = splitted_mail[0] + "@" + new_domain

    df["email_addresses"] = df["email_addresses"].replace(
        df[df.domains == target_domain].email_addresses.to_list(), corrected_mail
    )
    df["top_level_domains"] = (
        df["top_level_domains"]
        .replace(df[df.domains == target_domain].top_level_domains.to_list(), new_tld)
        .to_list()
    )
    df["domains"] = df["domains"].replace(
        df[df.domains == target_domain].domains.to_list(), new_domain
    )

    return df


def create_barplot(
    x_values: list, heights: list, title: str, x_label: str, y_label: str
) -> None:
    """
    Create and save a barplot with the passed values.

    Parameters
    ----------
    x_values : list
        The x coordinates of the bars.
    heights : list
        The height(s) of the bars.
    title : str
        Title of the barplot. Will be used as filename too.
    x_label : str
        Label on the x-axis.
    y_label : str
        Label on the y-axis.
    """
    plt.figure(figsize=(15, 8))
    axis = sns.barplot(x=x_values, y=heights)
    axis.set_xticklabels(axis.get_xticklabels(), rotation=30)
    axis.set_title(title)
    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)
    plt.savefig(
        TARGET_FOLDER.joinpath(f"{title}.{EXPORT_FILETYPE}"), bbox_inches="tight"
    )


def create_pieplot(
    x_values: list,
    labels: list,
    title: str,
    colors: str,
    figsize: tuple = (15, 8),
) -> None:
    """
    Create and save a pieplot with the passed values.

    Parameters
    ----------
    x_values : list
        The wedge sizes.
    labels : list
        A sequence of strings providing the labels for each wedge.
    title : str
        Title of the barplot. Will be used as filename too.
    colors : str
        A sequence of colors through which the pie chart will cycle
    figsize : tuple, optional
        Width, height in inches, by default (15, 8)
    """
    plt.figure(figsize=figsize)
    plt.pie(
        x=x_values,
        labels=labels,
        colors=colors,
        autopct="%.1f%%",
    )
    plt.title(title)
    plt.savefig(
        TARGET_FOLDER.joinpath(f"{title}.{EXPORT_FILETYPE}"), bbox_inches="tight"
    )


def create_world_plot(df: pd.DataFrame, title: str, figsize: tuple) -> None:
    """
    Create a world map with the passed dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Base dataframe enriched with geo data.
    title : str
        Title of the plot. Will be used as filename too.
    figsize : tuple
        Width, height in inches.
    """
    # initialize an axis
    fig, axis = plt.subplots(figsize=figsize)
    # plot map on axis
    countries = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
    countries.plot(color="lightgrey", ax=axis)
    df.plot(column="counts", figsize=figsize, legend=True, cmap="coolwarm", ax=axis)
    fig.suptitle(title, fontsize=50)
    fig.savefig(
        TARGET_FOLDER.joinpath(f"{title}.{EXPORT_FILETYPE}"), bbox_inches="tight"
    )


def get_domain_plot(df: pd.DataFrame, title: str, x_label: str, y_label: str) -> None:
    """
    Prepare data for the domain plot and create it.

    Parameters
    ----------
    df : pd.DataFrame
        Base dataframe with the columns email_addresses, domains and top_level_domains.
    title : str
        Title of the plot. Will be used as filename too.
    x_label : str
        Label on the x-axis.
    y_label : str
        Label on the y-axis.
    """
    domain_counts = df.domains.value_counts()
    unique_domains = domain_counts[domain_counts == 1]
    duplicated_domains = domain_counts[domain_counts > 1]
    duplicated_domain_dict = duplicated_domains.to_dict()
    duplicated_domain_dict["unique domains"] = len(unique_domains)
    create_barplot(
        x_values=list(duplicated_domain_dict.keys()),
        heights=list(duplicated_domain_dict.values()),
        title=title,
        x_label=x_label,
        y_label=y_label,
    )


def get_world_plot(df: DataFrame, title: str, figsize: tuple) -> dict:
    """
    Prepare data for the world plot and create the plot.

    Parameters
    ----------
    df : DataFrame
        Base dataframe with the columns email_addresses, domains and top_level_domains.
    title : str
        Title of the plot. Will be used as filename too.
    figsize : tuple
        Width, height in inches.

    Returns
    -------
    dict
        Country codes with the number of occurrences.
    """
    # Enrich the dataframe with additional geodata
    df["countries"] = get_country_list(df)
    df["country_codes"] = get_country_codes(df.countries)
    # We only want the entries with known countries
    df_w_known_email_origin = (df[df.country_codes != "Unknown"]).copy()
    # Add the number of appearances of each country
    country_counts = df_w_known_email_origin.country_codes.value_counts().to_dict()
    df_w_known_email_origin["counts"] = df_w_known_email_origin["country_codes"].map(
        country_counts
    )
    # Load the world map
    world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
    world.columns = WORLD_COLUMNS
    # Combine the dataframes
    location = pd.read_csv(COUNTRIES_LATITUDE_LONGITUDE)
    world_with_email_origin = pd.merge(
        world, df_w_known_email_origin, on="country_codes"
    )
    world_with_email_origin = world_with_email_origin.merge(
        location, on="name"
    ).reset_index()
    create_world_plot(world_with_email_origin, title, figsize)
    return country_counts  # We use this to create the pieplot later


def get_country_list(df: pd.DataFrame) -> list:
    """
    Resolve the origin of the mail addresses.

    Use the generic_domain_to_country and specific_domain_to_country mapping from mail_data.py to
    generate a the list of origins for each entry in the dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Base dataframe with the columns email_addresses, domains and top_level_domains.

    Returns
    -------
    list
        List with origins
    """
    country_list = []
    for domain, tld in df[["domains", "top_level_domains"]].itertuples(index=False):
        if domain in mail_data.GENERIC_DOMAINS_TO_COUNTRY:
            country = mail_data.GENERIC_DOMAINS_TO_COUNTRY[domain]
        elif tld in COUNTRY_SPECIFIC_DOMAINS_TO_COUNTRY:
            country = COUNTRY_SPECIFIC_DOMAINS_TO_COUNTRY.get(tld)
        else:
            country = "Unknown"

        country_list.append(country)
    return country_list


def get_country_codes(country_name_list: list) -> list:
    """
    Get the country codes for the passed country names.

    Parameters
    ----------
    country_name_list : list
        List with country names. Use "Unknown" for unknown countries.

    Returns
    -------
    list
        List with the corresponding country codes.
    """
    country_code_list = []
    for country in country_name_list:
        if country == "Unknown":
            country_code_list.append("Unknown")
        else:
            code = pycountry.countries.get(name=country).alpha_3
            country_code_list.append(code)
    return country_code_list


def main():
    """Short analysis of mail addresses."""
    # Load the data
    email_addresses = mail_data.EMAIL_ADDRESSES_STRING.split(";")
    df = get_base_df(email_addresses)

    # Cleanup shorthand and alternativ mail addresses
    df = rename_column_entries(df, "pm.me", "protonmail.com", "com")
    df = rename_column_entries(df, "googlemail.com", "gmail.com", "com")

    # Plot data (create_ methods create the plot, get_ methods are wrapper methods that first
    # prepare data and internally call the corresponding create_ method.)
    get_domain_plot(df, "Domains", "Domains", "Number of occurrences")

    top_level_domain_dict = df["top_level_domains"].value_counts().to_dict()
    create_barplot(
        x_values=list(top_level_domain_dict.keys()),
        heights=list(top_level_domain_dict.values()),
        title="top_level_domains",
        x_label="top_level_domains",
        y_label="count",
    )

    country_counts = get_world_plot(df, title="origin_worldmap", figsize=(25, 12.5))
    create_pieplot(
        list(country_counts.values()),
        list(country_counts.keys()),
        "origin_pieplot",
        sns.color_palette("coolwarm"),
        figsize=(15, 15),
    )


if __name__ == "__main__":
    main()
