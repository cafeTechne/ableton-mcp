{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 8,
      "minor": 6,
      "revision": 0,
      "architecture": "x64"
    },
    "classnamespace": "box",
    "rect": [ 92.0, 94.0, 480.0, 320.0 ],
    "bglocked": 0,
    "boxes": [
      {
        "box": {
          "id": "notein",
          "maxclass": "newobj",
          "numinlets": 0,
          "numoutlets": 3,
          "patching_rect": [ 40.0, 40.0, 46.0, 22.0 ],
          "text": "notein"
        }
      },
      {
        "box": {
          "id": "noteout",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 0,
          "patching_rect": [ 40.0, 100.0, 112.0, 22.0 ],
          "text": "noteout \"GameBus\""
        }
      },
      {
        "box": {
          "id": "ctlin",
          "maxclass": "newobj",
          "numinlets": 0,
          "numoutlets": 3,
          "patching_rect": [ 200.0, 40.0, 38.0, 22.0 ],
          "text": "ctlin"
        }
      },
      {
        "box": {
          "id": "ctlout",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 0,
          "patching_rect": [ 200.0, 100.0, 114.0, 22.0 ],
          "text": "ctlout \"GameBus\""
        }
      },
      {
        "box": {
          "id": "bendin",
          "maxclass": "newobj",
          "numinlets": 0,
          "numoutlets": 2,
          "patching_rect": [ 360.0, 40.0, 46.0, 22.0 ],
          "text": "bendin"
        }
      },
      {
        "box": {
          "id": "bendout",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 0,
          "patching_rect": [ 360.0, 100.0, 122.0, 22.0 ],
          "text": "bendout \"GameBus\""
        }
      }
    ],
    "lines": [
      { "patchline": { "source": [ "notein", 0 ], "destination": [ "noteout", 0 ] } },
      { "patchline": { "source": [ "notein", 1 ], "destination": [ "noteout", 1 ] } },
      { "patchline": { "source": [ "notein", 2 ], "destination": [ "noteout", 2 ] } },
      { "patchline": { "source": [ "ctlin", 0 ], "destination": [ "ctlout", 0 ] } },
      { "patchline": { "source": [ "ctlin", 1 ], "destination": [ "ctlout", 1 ] } },
      { "patchline": { "source": [ "ctlin", 2 ], "destination": [ "ctlout", 2 ] } },
      { "patchline": { "source": [ "bendin", 0 ], "destination": [ "bendout", 0 ] } },
      { "patchline": { "source": [ "bendin", 1 ], "destination": [ "bendout", 1 ] } }
    ]
  }
}
