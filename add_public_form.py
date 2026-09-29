import sys
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\login.html', 'r', encoding='utf-8') as f:
    content = f.read()

public_form = '''        <div class="mt-6 text-center">
            <p class="text-sm text-gray-600">
                Don't have an account? 
                <a href="/register" class="font-medium text-[#668054] hover:text-[#829c74]">Register here</a>
            </p>
        </div>
        
        <div class="mt-8">
            <div class="relative">
                <div class="absolute inset-0 flex items-center">
                    <div class="w-full border-t border-gray-200"></div>
                </div>
                <div class="relative flex justify-center text-sm">
                    <span class="px-2 bg-white text-gray-500 font-medium">Or view schedule (Irregular Students)</span>
                </div>
            </div>

            <form action="/public/timetable" method="GET" class="mt-6">
                <div class="flex gap-2">
                    <select name="section" required class="flex-1 focus:ring-[#668054] focus:border-[#668054] block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border outline-none">
                        <option value="">Select your section...</option>
                        {% for sec in sections %}
                        <option value="{{ sec }}">{{ sec }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit" class="inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gray-600 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-600 transition-colors">
                        View
                    </button>
                </div>
            </form>
        </div>
'''

content = content.replace('''        <div class="mt-6 text-center">
            <p class="text-sm text-gray-600">
                Don't have an account? 
                <a href="/register" class="font-medium text-[#668054] hover:text-[#829c74]">Register here</a>
            </p>
        </div>''', public_form)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\login.html', 'w', encoding='utf-8') as f:
    f.write(content)
