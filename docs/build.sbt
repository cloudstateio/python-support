lazy val docs = project
  .in(file("."))
  .enablePlugins(CloudstateParadoxPlugin)
  .settings(
    deployModule := "python",
    paradoxProperties in Compile ++= Map(
      "cloudstate.python.version" -> { if (isSnapshot.value) previousStableVersion.value.getOrElse("0.0.0") else version.value },
      "extref.cloudstate.base_url" -> "https://cloudstate.io/docs/core/current/%s"
    )
  )
