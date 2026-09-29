import sys
import re
with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\proctor_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

find_block = r'''                    <div class="space-y-6">
                        {% if grouped %}
                            {% for date, exams in grouped %}
                            <div class="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden">
                                <div class="bg-gray-50 px-6 py-3 border-b border-gray-200 font-semibold text-gray-700">
                                    {{ date }}
                                </div>
                                <div class="divide-y divide-gray-100">
                                    {% for exam in exams %}
                                    <div class="p-4 sm:px-6 hover:bg-gray-50">
                                        <div class="flex justify-between items-start">
                                            <div>
                                                <h4 class="text-md font-medium text-gray-900">{{ exam.subject_name }}</h4>
                                                <p class="text-sm text-gray-500 mt-1">Section: {{ exam.section }}</p>
                                            </div>
                                            <button onclick="openAbsenceModal\('{{ exam.id }}', '{{ exam.subject_name }} - {{ exam.section }}', '{{ date }}'\)" class="text-sm text-red-600 hover:text-red-800 font-medium bg-red-50 px-3 py-1 rounded-full border border-red-100">
                                                Report Absence
                                            </button>
                                        </div>
                                        <div class="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                                            <div class="flex items-center">
                                                <i class="fa-regular fa-clock mr-2 text-gray-400"></i>
                                                {{ exam.time }} \({{ \(exam.duration_minutes / 60\) \| round\(1\) }} hrs\)
                                            </div>
                                            <div class="flex items-center">
                                                <i class="fa-solid fa-door-open mr-2 text-gray-400"></i>
                                                {{ exam.room_name }}
                                            </div>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                            {% endfor %}'''

repl_block = '''                    <div class="space-y-10">
                        {% if grouped %}
                            {% for date, exams in grouped %}
                            <div>
                                <div class="flex items-center justify-between mb-4">
                                    <div class="inline-flex items-center gap-2 bg-[#668054] text-white text-sm font-bold tracking-wider uppercase px-4 py-2 rounded-lg shadow-sm">
                                        <i class="fa-regular fa-calendar-alt opacity-75"></i> {{ date }}
                                    </div>
                                    <div class="text-xs text-gray-500 font-medium">{{ exams|length }} exam{{ 's' if exams|length != 1 else '' }}</div>
                                </div>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {% for exam in exams %}
                                    <div class="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-lg transition-all relative">
                                        <div class="absolute top-4 right-4 flex items-center gap-1 text-[10px] font-bold text-green-600 uppercase tracking-wider">
                                            <i class="fa-solid fa-circle-check"></i> Confirmed
                                        </div>
                                        <h4 class="text-base font-bold text-gray-900 tracking-tight pr-20 mb-2.5">{{ exam.subject_name }}</h4>
                                        <div class="flex flex-wrap gap-1.5 mb-4">
                                            <span class="inline-flex items-center gap-1 bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                                                <i class="fa-solid fa-users text-blue-600"></i> {{ exam.section }}
                                            </span>
                                            <span class="inline-flex items-center gap-1 {% if exam.subject_type == 'Major' %}bg-green-100 text-green-800{% else %}bg-yellow-100 text-yellow-800{% endif %} px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                                                <i class="fa-solid fa-bookmark {% if exam.subject_type == 'Major' %}text-green-600{% else %}text-yellow-600{% endif %}"></i> {{ exam.subject_type }} Subject
                                            </span>
                                        </div>
                                        <div class="flex flex-col gap-2 mb-4">
                                            <div class="flex items-center gap-2 text-sm text-gray-700">
                                                <i class="fa-regular fa-clock w-4 text-center text-[#829c74]"></i>
                                                <span class="font-medium">{{ exam.time }} <span class="text-xs text-gray-400 ml-1">{{ exam.duration_minutes }} min</span></span>
                                            </div>
                                            <div class="flex items-center gap-2 text-sm text-gray-700">
                                                <i class="fa-solid fa-location-dot w-4 text-center text-[#829c74]"></i>
                                                <span class="font-medium">{{ exam.room_name or 'TBA' }}</span>
                                            </div>
                                        </div>
                                        <div class="border-t border-gray-100 pt-3 flex justify-end">
                                            <button onclick="openAbsenceModal('{{ exam.id }}', '{{ exam.subject_name }} - {{ exam.section }}', '{{ date }}')" class="inline-flex items-center text-xs font-medium text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg border border-red-100 transition-colors">
                                                <i class="fa-solid fa-triangle-exclamation mr-1.5 text-red-500"></i> Report Absence
                                            </button>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                            {% endfor %}'''

content = re.sub(find_block, repl_block, content)

with open('c:\\xamp2\\htdocs\\EXAM_MANAGEMENT\\template\\proctor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
