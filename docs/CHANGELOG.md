# Changelog

## 0.7.0

Feature:
* `load_file` to a Pandas dataframe, without SQL database dependencies [#77](https://github.com/astro-projects/astro/issues/77)

Documentation:
* Simplify README [#101](https://github.com/astro-projects/astro/issues/101)
* Add Release Guidelines [#160](https://github.com/astro-projects/astro/pull/160)
* Add Code of Conduct [#101](https://github.com/astro-projects/astro/pull/101)
* Add Contribution Guidelines [#101](https://github.com/astro-projects/astro/pull/101)

Enhancements:
* Add SQLite example [#149](https://github.com/astro-projects/astro/issues/149)
* Allow customization of `task_id` when using `dataframe` [#126](https://github.com/astro-projects/astro/issues/126)
* Use standard AWS environment variables, as opposed to `AIRFLOW__ASTRO__CONN_AWS_DEFAULT` [#175](https://github.com/astro-projects/astro/issues/175)

Bug fixes:
* Fix `merge` `XComArg` support [#183](https://github.com/astro-projects/astro/issues/183)
* Fixes to `load_file`:
   * `file_conn_id` support [#137](https://github.com/astro-projects/astro/issues/137)
   * `sqlite_default` connection support [#158](https://github.com/astro-projects/astro/issues/158)
* Fixes to `render`:
   * `conn_id` are optional in SQL files [#117](https://github.com/astro-projects/astro/issues/117)
   * `database` and `schema` are optional in SQL files [#124](https://github.com/astro-projects/astro/issues/124)
* Fix `transform`, so it works with SQLite [#159](https://github.com/astro-projects/astro/issues/159)

Others:
* Remove `transform_file` [#162](https://github.com/astro-projects/astro/pull/162)
* Improve integration tests coverage [#174](https://github.com/astro-projects/astro/pull/174)

## 0.6.0

Features:
* Support SQLite [#86](https://github.com/astro-projects/astro/issues/86)
* Support users who can't create schemas [#121](https://github.com/astro-projects/astro/issues/121)
* Ability to install optional dependencies (amazon, google, snowflake) [#82](https://github.com/astro-projects/astro/issues/82)

Enhancements:
* Change `render` so it creates a DAG as opposed to a TaskGroup [#143](https://github.com/astro-projects/astro/issues/143)
* Allow users to specify a custom version of `snowflake_sqlalchemy` [#127](https://github.com/astro-projects/astro/issues/127)

Bug fixes:
* Fix tasks created with `dataframe` so they inherit connection id [#134](https://github.com/astro-projects/astro/issues/134)
* Fix snowflake URI issues [#102](https://github.com/astro-projects/astro/issues/102)

Others:
* Run example DAGs as part of the CI [#114](https://github.com/astro-projects/astro/issues/114)
* Benchmark tooling to validate performance of `load_file` [#105](https://github.com/astro-projects/astro/issues/105)
