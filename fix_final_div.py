with open("template/settings.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace(
'''                    <p class="text-xs text-gray-500 mt-3">Tests the SMTP configuration currently saved in the system.</p>
                </div>
            </div>
        </div>
    </main>''',
'''                    <p class="text-xs text-gray-500 mt-3">Tests the SMTP configuration currently saved in the system.</p>
                </div>
            </div>
        </div>
        </div>
    </main>'''
)

with open("template/settings.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Added missing div!")
