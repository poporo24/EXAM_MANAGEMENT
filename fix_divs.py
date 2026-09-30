with open("template/settings.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix Scheduling Extra div
# The output currently looks like:
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#                 <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
# <button type="submit" ...>Save Scheduling Settings</button>
# </div>
# </form>

html = html.replace(
"""                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
<button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">Save Scheduling Settings</button>
</div>
</form>""",
"""                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save Scheduling Settings
                        </button>
                    </div>
                </form>"""
)

# Fix Exam Duration Extra div
html = html.replace(
"""                            </div>
                        </div>
                    </div>
                </div>
                    <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save Duration Settings
                        </button>
                    </div>
                </form>""",
"""                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                        <button type="submit" class="inline-flex justify-center py-2 px-6 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-[#668054] hover:bg-[#829c74]">
                            Save Duration Settings
                        </button>
                    </div>
                </form>"""
)

with open("template/settings.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Removed extra divs!")
