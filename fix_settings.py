import re

with open("template/settings.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix Scheduling Engine Settings
html = html.replace(
'''<p class="text-xs text-gray-500 mt-1">Maximum hours a proctor can serve without a break.</p>
                              </div>
                          </div>
                      </div>
                  </div>''',
'''<p class="text-xs text-gray-500 mt-1">Maximum hours a proctor can serve without a break.</p>
                              </div>
                          </div>
                      </div>
                      <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                          <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                              Save Scheduling Settings
                          </button>
                      </div>
                  </form>'''
)

# Fix Exam Duration Defaults
html = html.replace(
'''<p class="text-xs text-gray-500 mt-1">Default duration for Minor / Laboratory subjects.</p>
                            </div>
                        </div>
                    </div>
                </div>''',
'''<p class="text-xs text-gray-500 mt-1">Default duration for Minor / Laboratory subjects.</p>
                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save Duration Settings
                        </button>
                    </div>
                </form>'''
)

# Also fix the spacing around the next blocks. Currently "Change Password Settings" is stuck without a top margin if it's inside or outside space-y-8.
# Actually, the entire settings content is currently:
# <div class="space-y-8">
#   <form ... scheduling ...>
#   <form ... duration ...>
#   <form ... smtp ...>
# </div>
# Then <!-- Change Password Settings --> is outside the space-y-8?
# Let's put everything neatly in space-y-8.

html = html.replace('''            <!-- Test Email Section -->
            
                  <!-- Change Password Settings -->''',
'''            <!-- Change Password Settings -->''')

# Put the Change password into the space-y-8 if it isn't. 
# In the original, everything was inside the main container, but the single form wrapped the first 3.
# It seems my previous script left </div> right before <!-- Test Email Section -->.
html = html.replace('</form>\n            </div>\n\n            <!-- Change Password Settings -->', '</form>\n\n            <!-- Change Password Settings -->')
html = html.replace('<!-- Change Password Settings -->', '<!-- Change Password Settings -->')

with open("template/settings.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Fixed settings!")
