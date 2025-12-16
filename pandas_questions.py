"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(r"data/referendum.csv", sep=";")
    regions = pd.read_csv(r"data/regions.csv")
    departments = pd.read_csv(r"data/departments.csv")
    
    return referendum, regions, departments


def merge_regions_and_departments(df_reg, df_dep):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(df_dep, df_reg,
                                       left_on="region_code",  
                                       right_on="code",
                                       suffixes=("_dep", "_reg"))
    regions_and_departments = regions_and_departments.rename(
        columns={"code": "code_dep"}
        )
    regions_and_departments = regions_and_departments[["code_reg", 
                                                       "name_reg", 
                                                       "code_dep", 
                                                       "name_dep"]]

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    
    referendum = (
        referendum[~referendum["Department code"].str.contains("Z", na=False)]
    )
    s = regions_and_departments["code_dep"].astype(str).str.strip()
    regions_and_departments = (
        regions_and_departments[~s.str.fullmatch(r"\d{3}")].assign(
        code_dep=s.where(~s.str.fullmatch(r"\d+"), s.str.lstrip("0"))
        )
    )
    
    merge_referendum_and_areas = referendum.merge(regions_and_departments,
                         left_on="Department code", right_on="code_dep",
                         how="left")
    
    

    return merge_referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas["Town code"] = (
        referendum_and_areas["Town code"].astype(str)
    )

    return (
        referendum_and_areas
        .groupby("code_reg", as_index=True)
        .agg({
            "name_reg": "first",   
            "Registered": "sum",
            "Abstentions": "sum",
            "Null": "sum",
            "Choice A": "sum",
            "Choice B": "sum",
        })
    )


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson")
    gdf = gdf.rename(columns={"code": "code_reg"})
    map = gdf.merge(referendum_result_by_regions, on="code_reg", how="inner")
    map["ratio"] = map["Choice A"] / (map['Choice A'] + map["Choice B"])
    
    image = map.plot(column="ratio", legend=True)
    image.set_axis_off()
    plt.show()

    return map


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
