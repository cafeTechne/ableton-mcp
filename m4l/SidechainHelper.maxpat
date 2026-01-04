{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 8,
			"minor" : 5,
			"revision" : 6,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 150.0, 150.0, 640.0, 360.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "live.dial_source",
					"maxclass" : "live.dial",
					"numoutlets" : 1,
					"parameter_enable" : 1,
					"patching_rect" : [ 40.0, 60.0, 60.0, 60.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 10.0, 10.0, 60.0, 60.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.0 ],
							"parameter_mmin" : 0.0,
							"parameter_mmax" : 63.0,
							"parameter_shortname" : "Src Track",
							"parameter_longname" : "Source Track",
							"parameter_type" : 0
						}

					}
,
					"text" : "Source Track"
				}

			}
, 			{
				"box" : 				{
					"id" : "live.numbox_track",
					"maxclass" : "live.numbox",
					"numoutlets" : 2,
					"parameter_enable" : 1,
					"patching_rect" : [ 120.0, 60.0, 60.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 80.0, 10.0, 60.0, 20.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.0 ],
							"parameter_mmin" : 0.0,
							"parameter_mmax" : 63.0,
							"parameter_shortname" : "Target Track",
							"parameter_longname" : "Target Track",
							"parameter_type" : 0
						}

					}
,
					"text" : "Tgt Track"
				}

			}
, 			{
				"box" : 				{
					"id" : "live.numbox_device",
					"maxclass" : "live.numbox",
					"numoutlets" : 2,
					"parameter_enable" : 1,
					"patching_rect" : [ 120.0, 90.0, 60.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 80.0, 40.0, 60.0, 20.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.0 ],
							"parameter_mmin" : 0.0,
							"parameter_mmax" : 63.0,
							"parameter_shortname" : "Device",
							"parameter_longname" : "Target Device",
							"parameter_type" : 0
						}

					}
,
					"text" : "Device"
				}

			}
, 			{
				"box" : 				{
					"id" : "live.numbox_param",
					"maxclass" : "live.numbox",
					"numoutlets" : 2,
					"parameter_enable" : 1,
					"patching_rect" : [ 120.0, 120.0, 60.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 80.0, 70.0, 60.0, 20.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_initial" : [ 0.0 ],
							"parameter_mmin" : 0.0,
							"parameter_mmax" : 127.0,
							"parameter_shortname" : "Param",
							"parameter_longname" : "Parameter Index",
							"parameter_type" : 0
						}

					}
,
					"text" : "Param"
				}

			}
, 			{
				"box" : 				{
					"id" : "apply_button",
					"maxclass" : "textbutton",
					"numoutlets" : 1,
					"patching_rect" : [ 200.0, 60.0, 70.0, 30.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 150.0, 10.0, 70.0, 30.0 ],
					"text" : "Apply"
				}

			}
, 			{
				"box" : 				{
					"id" : "msg_path",
					"maxclass" : "message",
					"numinlets" : 3,
					"numoutlets" : 1,
					"patching_rect" : [ 200.0, 100.0, 200.0, 18.0 ],
					"text" : "path live_set tracks $1 devices $2 parameters $3"
				}

			}
, 			{
				"box" : 				{
					"id" : "msg_setvalue",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"patching_rect" : [ 200.0, 130.0, 100.0, 18.0 ],
					"text" : "set value $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "live.object",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"patching_rect" : [ 200.0, 160.0, 60.0, 22.0 ],
					"text" : "live.object"
				}

			}
, 			{
				"box" : 				{
					"id" : "plus_one",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"patching_rect" : [ 40.0, 130.0, 50.0, 20.0 ],
					"text" : "+ 1"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"source" : [ "apply_button", 0 ],
					"destination" : [ "msg_path", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"source" : [ "live.numbox_track", 0 ],
					"destination" : [ "msg_path", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"source" : [ "live.numbox_device", 0 ],
					"destination" : [ "msg_path", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"source" : [ "live.numbox_param", 0 ],
					"destination" : [ "msg_path", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"source" : [ "msg_path", 0 ],
					"destination" : [ "live.object", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"source" : [ "live.dial_source", 0 ],
					"destination" : [ "plus_one", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"source" : [ "plus_one", 0 ],
					"destination" : [ "msg_setvalue", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"source" : [ "msg_setvalue", 0 ],
					"destination" : [ "live.object", 0 ]
				}

			}
 ]
	}

}
